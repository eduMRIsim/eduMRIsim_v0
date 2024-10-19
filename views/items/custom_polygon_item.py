import math

import numpy as np
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPolygonF, QPen
from PyQt6.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsPixmapItem,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsSceneMouseEvent,
    QApplication,
    QGraphicsLineItem,
)

from events import EventEnum
from utils.logger import log


class CustomPolygonItem(QGraphicsPolygonItem):
    """Represents the intersection of the scan volume with the image in the viewer as a polygon. The polygon is movable and sends an update to the observers when it has been moved."""

    def __init__(self, parent: QGraphicsPixmapItem, viewer):
        super().__init__(parent)
        self.setPen(Qt.GlobalColor.yellow)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.observers = []
        self.previous_position_in_pixmap_coords = None
        self.slice_lines = []
        self.scan_volume = None
        self.displayed_image = None

        # Added viewer to update the scan view of the scan area with the selected rotation handler
        # It does not rotate when the other do without this viewer
        self.viewer = viewer

        # Parameters for rotation
        self.previous_handle_position = None
        self.is_rotating = False
        self.centroid = QPointF(0, 0)
        self.previous_angle = 0.0
        self.rotation_handle_offsets = None

        # Create the rotation handles. Use 8 in the case of polygon not being rectangular. Might not be accurate to real MRI, not sure how real machine handles this
        self.rotation_handles = []
        for i in range(8):
            handle = QGraphicsEllipseItem(-5, -5, 10, 10, parent=self)
            handle.setBrush(Qt.GlobalColor.yellow)
            handle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            handle.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            handle.setAcceptHoverEvents(True)
            handle.setCursor(Qt.CursorShape.OpenHandCursor)
            # Assign event handler to each handle
            handle.mousePressEvent = (
                lambda event, h=handle: self.handle_rotation_handle_press(event, h)
            )
            self.rotation_handles.append(handle)

        # Initial positioning of the rotation handle
        self.update_rotation_handle_positions()

        # Scale parameters, including scale handles.
        self.is_being_scaled = False
        self.scale_handles = []
        for i in range(8):
            handle = QGraphicsEllipseItem(-5, -5, 10, 10, parent=self)
            handle.setPen(Qt.GlobalColor.yellow)
            handle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, enabled=False)
            handle.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            handle.setAcceptHoverEvents(True)
            handle.setCursor(Qt.CursorShape.PointingHandCursor)
            handle.mousePressEvent = (
                lambda event, hdl=handle: self.scale_handle_press_event_handler(
                    event, hdl
                )
            )
            self.scale_handles.append(handle)
        self.scale_handle_offsets = []
        self.active_scale_handle = None
        self.scene_center = QPointF(0.0, 0.0)
        self.previous_scale_handle_position = (0.0, 0.0)

        self.scaling_vector_components = (1.0, 1.0, 1.0)
        self.scaling_side = None

        # Set the initial position of the scale handles.
        self.update_scale_handle_positions()

    def setScanVolume(self, scan_volume):
        self.scan_volume = scan_volume

    def update_rotation_handle_positions(self):
        """Update the positions of the rotation handlers"""
        if self.polygon().isEmpty() or not self.rotation_handle_offsets:
            return
        if not self.isVisible():
            for handle in self.rotation_handles:
                handle.setVisible(False)
            return

        if self.polygon().isEmpty() or not self.rotation_handle_offsets:
            for handle in self.rotation_handles:
                handle.setVisible(False)
            return

        polygon = self.polygon()
        n_points = len(polygon)

        # Calculate centroid in local coordinates
        centroid_x = sum(point.x() for point in polygon) / n_points
        centroid_y = sum(point.y() for point in polygon) / n_points
        centroid_local = QPointF(centroid_x, centroid_y)

        # Update each rotation handle position
        for i, offset in enumerate(self.rotation_handle_offsets):
            if i >= len(self.rotation_handles):
                break
            handle = self.rotation_handles[i]
            handle_pos_local = centroid_local + offset
            handle.setPos(handle_pos_local)
            handle.setVisible(True)

        # Hide any extra handles
        for i in range(len(self.rotation_handle_offsets), len(self.rotation_handles)):
            self.rotation_handles[i].setVisible(False)

        # Initialize previous handle position in scene coordinates
        if self.previous_handle_position is None and self.rotation_handles:
            self.previous_handle_position = self.mapToScene(
                self.rotation_handles[0].pos()
            )

    # Custom setVisible for rotation handles
    def setVisible(self, visible: bool):
        super().setVisible(visible)
        for handle in self.rotation_handles:
            handle.setVisible(visible)

    def update_scale_handle_positions(self):
        """
        This function updates the scale handle positions so that they are moved to their new positions.
        """

        # Get the current polygon and its number of points.
        polygon = self.polygon()
        number_of_points = len(polygon)

        # Error case, avoids division by zero.
        if number_of_points == 0:
            return

        # Find the local center of the polygon's points.
        local_center = QPointF(
            sum(point.x() for point in polygon) / number_of_points,
            sum(point.y() for point in polygon) / number_of_points,
        )

        # Set the new handle positions based on the local center and the offsets.
        # Also, show only the first few handles.
        for i, offset in enumerate(self.scale_handle_offsets):
            if i >= len(self.scale_handles):
                break
            handle = self.scale_handles[i]
            handle_pos_local = local_center + offset
            handle.setPos(handle_pos_local)
            handle.setVisible(True)

        # Hide the remaining handles.
        for i in range(len(self.scale_handle_offsets), len(self.scale_handles)):
            self.scale_handles[i].setVisible(False)

    def scale_handle_press_event_handler(self, event: QGraphicsSceneMouseEvent, handle):
        """
        This function is an event handler that is called whenever the user left-clicks on a scale handle.
        :param event: the mouse event that the user performed by left-clicking on a scale handle.
        :param handle: the scale handle that the user clicked on.
        """
        # Set the scale handle as active and change the cursor to a closed hand.
        self.is_being_scaled = True
        self.active_scale_handle = handle  # Keep track of which handle is active.
        self.previous_scale_handle_position = (event.scenePos().x(), event.scenePos().y())
        handle.setCursor(Qt.CursorShape.ClosedHandCursor)

        # Determine scaling vector's components based on the handle position
        self.scaling_vector_components, self.scaling_side = self.determine_vector_axis(self.previous_scale_handle_position)
        self.previous_handle_position = self.viewer.displayed_image.image_geometry.pixmap_coords_to_LPS_coords((self.previous_scale_handle_position[0], self.previous_scale_handle_position[1]))
        log.debug(f"Scaling vector components: {self.scaling_vector_components}")
        log.debug(f"Scaling side: {self.scaling_side}")

    def determine_vector_axis(self, handle_position):
        corners = self.scan_volume.compute_intersection_with_acquired_image(self.displayed_image)[0]
        x = handle_position[0]
        y = handle_position[1]
        edge_number = -1
        scaling_vector = None
        for i in range(len(corners)):
            if i == len(corners) -1:
                j = 0
            else:
                j = i + 1
            if abs((corners[i][0] + corners[j][0])/2 - x) <= 5 and abs((corners[i][1] + corners[j][1])/2 - y)<= 5:
                edge_number = i
                log.debug(f"Edge number: {i}")
                
                # Determine the edge by endpoints, it's vector representation and the middle point of it
                corner_1 = self.viewer.displayed_image.image_geometry.pixmap_coords_to_LPS_coords(corners[i])
                corner_2 = self.viewer.displayed_image.image_geometry.pixmap_coords_to_LPS_coords(corners[j])

                # Determine mid point and 3D vector of the edge
                mid_point = ((corner_1[0] + corner_2[0])/2, (corner_1[1] + corner_2[1])/2, (corner_1[2] + corner_2[2])/2)
                edge_3d_vector = tuple(map(lambda i, k: i-k, corner_2, corner_1))

                # Determine the plane perpendicular to the edge
                perpendicular_plane = self.perpendicular_plane_to_vector(edge_3d_vector, mid_point)

                # Determine the plane of the image
                plane_plane = self.plane_from_vectors(self.viewer.displayed_image.image_geometry.axisX_LPS, self.viewer.displayed_image.image_geometry.axisY_LPS, mid_point)

                # Determine the intersection of the two planes
                intersection = self.intersection_of_planes(perpendicular_plane, plane_plane)

                # Determine the scaling vector by normalizing the intersection vector
                scaling_vector = self.convert_vector_to_proportions_LPS(intersection[1])
                break
            
        
        # If edge couldn't be determined
        if edge_number == -1:
            return RuntimeError("Could not determine edge number")
        
        return scaling_vector, edge_number

    def perpendicular_plane_to_vector(self, vector, point):
        """
        Given a 3D vector and a point, this function returns the equation of the plane 
        perpendicular to the vector and passing through the point.
        
        :param vector: A tuple or list with the components of the 3D vector (v_x, v_y, v_z)
        :param point: A tuple or list with the coordinates of the point (x_0, y_0, z_0)
        :return: A tuple (A, B, C, D) which are the coefficients of the plane equation: Ax + By + Cz = D
        """
        v_x, v_y, v_z = vector
        x_0, y_0, z_0 = point
        
        # Calculate D using the point and vector (the normal of the plane)
        D = v_x * x_0 + v_y * y_0 + v_z * z_0
        
        # Return the coefficients of the plane equation
        return (v_x, v_y, v_z, D)
    
    def plane_from_vectors(self, v1, v2, point):
        """
        Given two vectors v1 and v2, and a point on the plane,
        this function computes the equation of the plane in the form:
        A*x + B*y + C*z = D
        
        :param v1: A tuple or list with the components of the first vector (x1, y1, z1)
        :param v2: A tuple or list with the components of the second vector (x2, y2, z2)
        :param point: A tuple or list with the coordinates of a point on the plane (x0, y0, z0)
        :return: A tuple (A, B, C, D) which are the coefficients of the plane equation: Ax + By + Cz = D
        """
        
        # Convert the vectors to numpy arrays for easy computation
        v1 = np.array(v1)
        v2 = np.array(v2)
        
        # Compute the normal vector to the plane (cross product of v1 and v2)
        normal = np.cross(v1, v2)
        A, B, C = normal
        
        # Extract the point on the plane (x0, y0, z0)
        x0, y0, z0 = point
        
        # Calculate D using the point and the normal vector
        D = A * x0 + B * y0 + C * z0
        
        # Return the plane equation coefficients
        return A, B, C, D
    
    def intersection_of_planes(self, plane1, plane2):
        """
        Given two planes in the form (A1, B1, C1, D1) and (A2, B2, C2, D2),
        this function calculates the line of intersection between the two planes.
        
        The planes are of the form:
        A1*x + B1*y + C1*z = D1 (Plane 1)
        A2*x + B2*y + C2*z = D2 (Plane 2)
        
        The function returns the parametric equation of the line in the form:
        x = x0 + t * dx
        y = y0 + t * dy
        z = z0 + t * dz
        """
        
        # Extract coefficients of the planes
        A1, B1, C1, D1 = plane1
        A2, B2, C2, D2 = plane2
        
        # Normal vectors of the two planes
        normal1 = np.array([A1, B1, C1])
        normal2 = np.array([A2, B2, C2])
        
        # The direction of the line of intersection is the cross product of the normals
        direction = np.cross(normal1, normal2)
        
        # If the direction is a zero vector, the planes are parallel or identical
        if np.all(direction == 0):
            raise ValueError("The planes are either parallel or identical, so there is no unique line of intersection.")
        
        # Find a point on the line by solving the system of equations
        # We'll eliminate one of the variables (e.g., z) and solve for x and y

        # Create coefficient matrix for the system of equations with z = 0
        A = np.array([[A1, B1], [A2, B2]])
        b = np.array([D1, D2])

        # Check if A is invertible (non-singular) for solving x and y
        if np.linalg.det(A) != 0:
            # Solve for x and y when z = 0
            x0, y0 = np.linalg.solve(A, b)
            z0 = 0
        else:
            # If the above fails (planes are perpendicular to x or y axes), try setting x = 0 or y = 0
            A = np.array([[A1, C1], [A2, C2]])
            b = np.array([D1, D2])

            if np.linalg.det(A) != 0:
                # Solve for x and z when y = 0
                x0, z0 = np.linalg.solve(A, b)
                y0 = 0
            else:
                # Solve for y and z when x = 0
                A = np.array([[B1, C1], [B2, C2]])
                b = np.array([D1, D2])
                y0, z0 = np.linalg.solve(A, b)
                x0 = 0

        # Return the parametric form of the line: point (x0, y0, z0) and direction vector (dx, dy, dz)
        return (x0, y0, z0), direction
    
    def convert_vector_to_proportions_LPS(self, vector):
        sum = np.linalg.norm(vector)
        return (abs(vector[0])/sum, abs(vector[1])/sum, abs(vector[2])/sum)
    
    def make_parallel(self, v, d):
        # Convert vectors to numpy arrays
        v = np.array(v)
        d = np.array(d)
        
        # Calculate the magnitude of the direction vector
        d_magnitude = np.linalg.norm(d)
        
        # If the direction vector is zero, return a zero vector
        if d_magnitude == 0:
            return np.zeros_like(v)
        
        # Calculate the scalar projection of v onto d
        scalar_projection = np.dot(v, d) / d_magnitude
        
        # Scale the direction vector by the projection and normalize it
        parallel_vector = (scalar_projection / d_magnitude) * d
        
        return parallel_vector

    def scale_handle_move_event_handler(self, event: QGraphicsSceneMouseEvent):
        """
        This function is called whenever a scale handle is moved,
        i.e. when the user holds left click on and drags a scale handle to a new position.
        :param event: the mouse event that the user performed by holding left click on and dragging a scale handle.
        """

        # Get the new position in scene coordinates.
        new_position = event.scenePos()
        #print(f"Cursor position: {new_position.x()}, {new_position.y()}")
        handle_position = None
        
        # Get the new locaiton of the handle.
        corners = self.scan_volume.compute_intersection_with_acquired_image(self.displayed_image)[0]
        if self.scaling_side == len(corners)-1:
            handle_position = ((corners[self.scaling_side][0] + corners[0][0]) / 2, (corners[self.scaling_side][1] + corners[0][1]) / 2)
        else:
            handle_position = ((corners[self.scaling_side][0] + corners[self.scaling_side + 1][0]) / 2, (corners[self.scaling_side][1] + corners[self.scaling_side + 1][1]) / 2)

        # Convert positions to LPS coordinates
        log.debug(f"Handle position: {handle_position}")
        log.debug(f"Cursor position: {new_position.x()}, {new_position.y()}")    
        new_position_LPS = self.viewer.displayed_image.image_geometry.pixmap_coords_to_LPS_coords((new_position.x(), new_position.y()))
        handle_position_LPS = self.viewer.displayed_image.image_geometry.pixmap_coords_to_LPS_coords((handle_position[0], handle_position[1]))
        log.debug(f"Cursor position LPS: {new_position_LPS}")
        log.debug(f"Handle position LPS: {handle_position_LPS}")

        # Align new position vector with direction vector
        difference_vector = tuple(map(lambda i, k: i-k, new_position_LPS, handle_position_LPS))
        log.debug(f"Difference vector: {difference_vector}")
        difference_vector_aligned = self.make_parallel(difference_vector, self.scaling_vector_components)
        log.debug(f"Difference vector aligned: {difference_vector_aligned}")
        
        # Assign the vector axis to seperate variables
        x_move = difference_vector_aligned[0]
        y_move = difference_vector_aligned[1]
        z_move = difference_vector_aligned[2]

        # Decide on the direction of scale
        if new_position_LPS[0] < 0 and handle_position_LPS[0] < 0:
            x_move = -x_move
        if new_position_LPS[1] < 0 and handle_position_LPS[1] < 0:
            y_move = -y_move
        if new_position_LPS[2] < 0 and handle_position_LPS[2] < 0:
            z_move = -z_move


        #print(f"X: {x_move}, Y: {y_move}, Z: {z_move}")
        # Limit maximum movement
        limit = 15#float('inf')
        if abs(x_move) > limit:
            x_move = limit if x_move > 0 else -limit
        if abs(y_move) > limit:
            y_move = limit if y_move > 0 else -limit
        if abs(z_move) > limit:
            z_move = limit if z_move > 0 else -limit


        # Set the previous handle position equal to the new handle position.
        self.previous_scale_handle_position = handle_position_LPS

        # Save sizes for check
        previous_sizes = (self.scan_volume.extentX_mm, self.scan_volume.extentY_mm, self.scan_volume.slice_gap_mm)

        # Let the other windows know that the scan volume display was scaled, passing in the calculated scale factors.
        self.notify_observers(
            EventEnum.SCAN_VOLUME_DISPLAY_SCALED,
            x_vector=x_move,
            y_vector=y_move,
            z_vector=z_move
        )

        # Update the scale handle positions.
        self.update_scale_handle_positions()

        # Check if size has been updated
        if previous_sizes == (self.scan_volume.extentX_mm, self.scan_volume.extentY_mm, self.scan_volume.slice_gap_mm):
            self.is_being_scaled = False
        
        print(self.is_being_scaled)

    def scale_handle_release_event_handler(self):
        """
        This function is called whenever a scale handle is released,
        i.e. when the user stops holding left click on the scale handle.
        """

        self.is_being_scaled = False

        self.scaling_vector_components = (1.0, 1.0, 1.0)
        self.scaling_side = None

        # Reset the active scale handle if it was set previously.
        if self.active_scale_handle is not None:
            self.active_scale_handle.setCursor(Qt.CursorShape.PointingHandCursor)
            self.active_scale_handle = None

    def get_plane_axis(self):
        """Determine the rotation axis based on the displayed image plane"""
        plane = self.viewer.displayed_image.image_geometry.plane

        if plane is None:
            raise ValueError("Image plane is not set in ImageGeometry.")

        plane = plane.lower()

        if plane == "axial":
            return "FH"
        elif plane == "sagittal":
            return "RL"
        elif plane == "coronal":
            return "AP"
        else:
            raise ValueError(f"Unknown plane: {plane}")

    def setPolygon(self, polygon_in_polygon_coords: QPolygonF):
        n_points = len(polygon_in_polygon_coords)
        # If the polygon is empty, clear the rotation and scaling handles, and exit early. This check prevents a crash
        if n_points == 0:
            super().setPolygon(polygon_in_polygon_coords)
            for handle in self.rotation_handles:
                handle.setVisible(False)
            self.rotation_handle_offsets = []
            for handle in self.scale_handles:
                handle.setVisible(False)
            self.scale_handle_offsets = []
            return
        super().setPolygon(polygon_in_polygon_coords)
        self.previous_position_in_pixmap_coords = self.pos()

        # Calculate centroid in local coordinates
        centroid_x = sum(point.x() for point in polygon_in_polygon_coords) / n_points
        centroid_y = sum(point.y() for point in polygon_in_polygon_coords) / n_points
        centroid_polygon = QPointF(centroid_x, centroid_y)

        # Compute the offsets for each corner
        self.rotation_handle_offsets = []
        for i in range(n_points):
            corner_point = polygon_in_polygon_coords[i]
            offset = corner_point - centroid_polygon
            self.rotation_handle_offsets.append(offset)

        # Update rotation handles positions
        self.update_rotation_handle_positions()

        # Calculate offset and update position for scale handles
        local_center = QPointF(
            sum(point.x() for point in polygon_in_polygon_coords) / n_points,
            sum(point.y() for point in polygon_in_polygon_coords) / n_points,
        )

        self.scale_handle_offsets = []
        for i in range(n_points):
            offset = (
                polygon_in_polygon_coords[i]
                + polygon_in_polygon_coords[(i + 1) % n_points]
            ) / 2 - local_center
            self.scale_handle_offsets.append(offset)

        self.update_scale_handle_positions()

    def setPolygonFromPixmapCoords(self, polygon_in_pixmap_coords: list[np.array]):
        polygon_in_polygon_coords = QPolygonF()
        for pt in polygon_in_pixmap_coords:
            pt_in_polygon_coords = self.mapFromParent(QPointF(pt[0], pt[1]))
            polygon_in_polygon_coords.append(pt_in_polygon_coords)
        self.setPolygon(polygon_in_polygon_coords)

    def add_observer(self, observer: object):
        self.observers.append(observer)
        log.debug(f"Observer {observer} added to {self}")

    def notify_observers(self, event: EventEnum, **kwargs):
        for observer in self.observers:
            log.debug(
                f"Subject {self} is updating observer {observer} with event {event}"
            )
            observer.update(event, **kwargs)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        direction_vector_in_pixmap_coords = QPointF(
            self.pos().x() - self.previous_position_in_pixmap_coords.x(),
            self.pos().y() - self.previous_position_in_pixmap_coords.y(),
        )
        self.previous_position_in_pixmap_coords = self.pos()
        self.update_scale_handle_positions()
        direction_vec_in_lps = (
            self.viewer.handle_calculate_direction_vector_from_move_event(
                direction_vector_in_pixmap_coords
            )
        )
        # apply volume updates also for current scan planning window polygon
        self.viewer._update_scan_volume_display()
        self.notify_observers(
            EventEnum.SCAN_VOLUME_DISPLAY_TRANSLATED,
            direction_vector_in_lps_coords=direction_vec_in_lps,
        )

    # on press show "size all" cursor
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        super().mousePressEvent(event)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    # on release show "pointing hand" cursor
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # on hover show "pointing hand" cursor
    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # on leave change cursor to default
    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.unsetCursor()

    # Detecting mouse for rotation. Uses scene events since other method did not work
    def handle_rotation_handle_press(self, event: QGraphicsSceneMouseEvent, handle):
        """Initiate rotation when the rotation handle is pressed"""
        self.is_rotating = True
        self.active_handle = handle  # Keep track of which handle is active
        self.previous_handle_position = event.scenePos()
        handle.setCursor(Qt.CursorShape.ClosedHandCursor)

        # Calculate centroid in scene coordinates
        polygon = self.polygon()
        if polygon.isEmpty():
            self.centroid = QPointF(0, 0)
        else:
            centroid_local = QPointF(
                sum(point.x() for point in polygon) / len(polygon),
                sum(point.y() for point in polygon) / len(polygon),
            )
            self.centroid = self.mapToScene(centroid_local)

        # Calculate initial angle
        dx = self.previous_handle_position.x() - self.centroid.x()
        dy = self.previous_handle_position.y() - self.centroid.y()
        self.previous_angle = math.atan2(dy, dx)

    def handle_scene_mouse_move(self, event: QGraphicsSceneMouseEvent):
        if not self.is_rotating:
            return

        new_pos = event.scenePos()
        dx = new_pos.x() - self.centroid.x()
        dy = new_pos.y() - self.centroid.y()
        new_angle = math.atan2(dy, dx)

        angle_diff_rad = new_angle - self.previous_angle
        angle_diff_rad = (angle_diff_rad + math.pi) % (2 * math.pi) - math.pi
        angle_diff_deg = math.degrees(angle_diff_rad)

        self.previous_angle = new_angle
        self.previous_handle_position = new_pos

        rotation_axis = self.get_rotation_axis()

        self.notify_observers(
            EventEnum.SCAN_VOLUME_DISPLAY_ROTATED,
            rotation_angle_deg=angle_diff_deg,
            rotation_axis=rotation_axis,
        )

        # Update display so the currently selected polygon also rotates
        self.viewer._update_scan_volume_display()
        self.viewer.viewport().update()
        QApplication.processEvents()
        self.update_rotation_handle_positions()

    def handle_scene_mouse_release(self, event: QGraphicsSceneMouseEvent):
        self.is_rotating = False
        if hasattr(self, "active_handle") and self.active_handle:
            self.active_handle.setCursor(Qt.CursorShape.OpenHandCursor)
            self.active_handle = None

    def get_rotation_axis(self):
        """Determine the rotation axis based on the displayed image plane"""
        plane = self.viewer.displayed_image.image_geometry.plane

        if plane is None:
            raise ValueError("Image plane is not set in ImageGeometry.")

        plane = plane.lower()

        if plane == "axial":
            return "FH"
        elif plane == "sagittal":
            return "RL"
        elif plane == "coronal":
            return "AP"
        else:
            raise ValueError(f"Unknown plane: {plane}")

    def set_scan_volume(self, scan_volume):
        self.scan_volume = scan_volume
        # self.update_slice_lines()

    def set_displayed_image(self, displayed_image):
        self.displayed_image = displayed_image
        # self.update_slice_lines()

    def update_slice_lines(self):
        # Remove existing slice lines
        for line in self.slice_lines:
            self.scene().removeItem(line)
        self.slice_lines.clear()

        if (
            not self.scan_volume
            or not self.displayed_image
            or not self._are_slices_visible()
        ):
            return

        polygon = self.polygon()
        if polygon.isEmpty() or polygon.size() < 4:
            return

        slice_positions = self.scan_volume.calculate_slice_positions()
        total_thickness = self.scan_volume.extentZ_mm

        for z in slice_positions:
            relative_pos = (z + total_thickness / 2) / total_thickness
            start = self._interpolate_point(polygon[0], polygon[3], relative_pos)
            end = self._interpolate_point(polygon[1], polygon[2], relative_pos)

            line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y(), self)
            line.setPen(QPen(Qt.GlobalColor.red, 1))
            self.slice_lines.append(line)

    def _are_slices_visible(self):
        if not self.displayed_image or not self.scan_volume:
            return False

        image_normal = np.array(self.displayed_image.image_geometry.axisZ_LPS)
        slice_direction = np.array(self.scan_volume.axisZ_LPS)
        dot_product = np.abs(np.dot(image_normal, slice_direction))
        return dot_product > 0.3

    def _interpolate_point(self, p1, p2, t):
        return QPointF(p1.x() + (p2.x() - p1.x()) * t, p1.y() + (p2.y() - p1.y()) * t)
