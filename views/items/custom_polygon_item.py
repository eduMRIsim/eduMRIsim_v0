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
        self.previous_scale_handle_position = None

        self.on_x_axis = False
        self.on_y_axis = False

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

        self.is_being_scaled = True
        self.active_scale_handle = handle  # Keep track of which handle is active.
        self.previous_scale_handle_position = event.scenePos()
        handle.setCursor(Qt.CursorShape.ClosedHandCursor)

        # Get the current polygon (points), and the number of points in the current polygon.
        polygon = self.polygon()
        number_of_points = len(polygon)

        # If the current polygon has no points, the scene center will be (0.0, 0.0) in scene coordinates;
        # else, the scene center is the center of all points in the polygon.
        if number_of_points == 0:
            self.scene_center = QPointF(0.0, 0.0)
        else:
            self.scene_center = QPointF(
                sum(point.x() for point in polygon) / number_of_points,
                sum(point.y() for point in polygon) / number_of_points,
            )
            self.scene_center = self.mapToScene(self.scene_center)

        self.on_x_axis = (
            abs(self.previous_scale_handle_position.x() - self.scene_center.x()) <= 5.5
        )
        self.on_y_axis = (
            abs(self.previous_scale_handle_position.y() - self.scene_center.y()) <= 5.5
        )

        rotations = self.scan_volume.get_rotations()
        plane = self.get_plane_axis()  # FH = Axial, RL = Sagittal, AP = Coronal
        log.debug(
            f"{rotations} {plane}, {self.previous_handle_position}, {self.scene_center}"
        )

        if plane == "FH" and rotations["FHAngle_rad"] != 0:
            self.on_x_axis, self.on_y_axis = self.determine_axis_to_scale(
                "Axial",
                self.previous_scale_handle_position,
                self.scene_center,
                rotations["RLAngle_rad"],
                rotations["APAngle_rad"],
                rotations["FHAngle_rad"],
            )
        elif plane == "RL" and rotations["RLAngle_rad"] != 0:
            self.on_x_axis, self.on_y_axis = self.determine_axis_to_scale(
                "Sagittal",
                self.previous_scale_handle_position,
                self.scene_center,
                rotations["RLAngle_rad"],
                rotations["APAngle_rad"],
                rotations["FHAngle_rad"],
            )
        elif plane == "AP" and rotations["APAngle_rad"] != 0:
            self.on_x_axis, self.on_y_axis = self.determine_axis_to_scale(
                "Coronal",
                self.previous_scale_handle_position,
                self.scene_center,
                rotations["RLAngle_rad"],
                rotations["APAngle_rad"],
                rotations["FHAngle_rad"],
            )

        # The logic for determining which axis the user is scaling on TBD
        log.debug(f"{self.on_x_axis}, {self.on_y_axis}")

    def determine_axis_to_scale(
        self,
        origin_plane,
        handle_pos,
        center_pos,
        RLAngle_rad,
        APAngle_rad,
        FHAngle_rad,
    ):
        log.debug(
            f"{origin_plane}, {handle_pos}, {center_pos}, {RLAngle_rad}, {APAngle_rad}, {FHAngle_rad}"
        )
        converter = 180 / math.pi
        if origin_plane == "Sagittal":  # around RL axis
            # Rotation to positive direction
            if RLAngle_rad * converter < 90 and RLAngle_rad * converter > 0:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
            elif RLAngle_rad * converter >= 90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
            # Rotation to negative direction
            elif RLAngle_rad * converter < 0 and RLAngle_rad * converter > -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
            elif RLAngle_rad * converter <= -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
        elif origin_plane == "Coronal":  # around AP axis
            # Rotation to positive direction
            if APAngle_rad * converter <= 90 and APAngle_rad * converter > 0:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
            elif APAngle_rad * converter > 90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
            # Rotation to negative direction
            elif APAngle_rad * converter < 0 and APAngle_rad * converter > -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
            elif APAngle_rad * converter <= -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
        elif origin_plane == "Axial":  # around FH axis
            # Rotation to positive direction
            if FHAngle_rad * converter < 90 and FHAngle_rad * converter > 0:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
            elif FHAngle_rad * converter >= 90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
            # Rotation to negative direction
            elif FHAngle_rad * converter < 0 and FHAngle_rad * converter > -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
            elif FHAngle_rad * converter <= -90:
                if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                    return False, True
                if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                    return True, False
                if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                    return False, True
        return False, False

    def scale_handle_move_event_handler(self, event: QGraphicsSceneMouseEvent):
        """
        This function is called whenever a scale handle is moved,
        i.e. when the user holds left click on and drags a scale handle to a new position.
        :param event: the mouse event that the user performed by holding left click on and dragging a scale handle.
        """

        # Get the new position in scene coordinates.
        new_position = event.scenePos()

        # Calculate the scale factors in the x and y directions.
        # Also, avoid division by zero, which would happen if the previous scale handle position's x or y is equal to
        # the scene center's x or y respectively; in that case, set the respective scale factor to 1.0.
        if (
            self.on_x_axis
            or abs(self.previous_scale_handle_position.x() - self.scene_center.x()) == 0
        ):
            scale_factor_x = 1.0
        else:
            scale_factor_x = abs(new_position.x() - self.scene_center.x()) / abs(
                self.previous_scale_handle_position.x() - self.scene_center.x()
            )
            if scale_factor_x <= 0.92 or scale_factor_x >= 1.08:
                scale_factor_x = 1.0
        if (
            self.on_y_axis
            or abs(self.previous_scale_handle_position.y() - self.scene_center.y()) == 0
        ):
            scale_factor_y = 1.0
        else:
            scale_factor_y = abs(new_position.y() - self.scene_center.y()) / abs(
                self.previous_scale_handle_position.y() - self.scene_center.y()
            )
            if scale_factor_y <= 0.92 or scale_factor_y >= 1.08:
                scale_factor_y = 1.0

        # Set the previous handle position equal to the new handle position.
        self.previous_scale_handle_position = new_position

        # Let the other windows know that the scan volume display was scaled, passing in the calculated scale factors.
        self.notify_observers(
            EventEnum.SCAN_VOLUME_DISPLAY_SCALED,
            scale_factor_x=scale_factor_x,
            scale_factor_y=scale_factor_y,
            origin_plane=self.viewer.displayed_image.image_geometry.plane,
            handle_pos=self.active_scale_handle.pos(),
            center_pos=self.scene_center,
        )

        # Update the scale handle positions.
        self.update_scale_handle_positions()

    def scale_handle_release_event_handler(self):
        """
        This function is called whenever a scale handle is released,
        i.e. when the user stops holding left click on the scale handle.
        """

        self.is_being_scaled = False
        self.on_x_axis = False
        self.on_y_axis = False

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

        # Access the rotation parameters of the plane the rotation is being performed on
        image_geometry = self.viewer.displayed_image.image_geometry
        RLAngle_deg = image_geometry.RLAngle_deg
        APAngle_deg = image_geometry.APAngle_deg
        FHAngle_deg = image_geometry.FHAngle_deg

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

        # Compute the projected rotation angle
        incremental_angles_deg = compute_projected_rotation(
            angle_diff_deg,
            RLAngle_deg,
            APAngle_deg,
            FHAngle_deg,
            rotation_axis,
        )

        # Extract rotations for each seperate angle
        incremental_RL_angle = incremental_angles_deg[0]
        incremental_AP_angle = incremental_angles_deg[1]
        incremental_FH_angle = incremental_angles_deg[2]


        # Send signals for each angle
        # A check for greater than 1e-6 to delete very small values of noise which can get generated due to calculation and rounding errors
        if abs(incremental_RL_angle) > 1e-6:
            self.notify_observers(
                EventEnum.SCAN_VOLUME_DISPLAY_ROTATED,
                rotation_angle_deg=incremental_RL_angle,
                rotation_axis='RL',
            )

        if abs(incremental_AP_angle) > 1e-6:
            self.notify_observers(
                EventEnum.SCAN_VOLUME_DISPLAY_ROTATED,
                rotation_angle_deg=incremental_AP_angle,
                rotation_axis='AP',
            )

        if abs(incremental_FH_angle) > 1e-6:
            self.notify_observers(
                EventEnum.SCAN_VOLUME_DISPLAY_ROTATED,
                rotation_angle_deg=incremental_FH_angle,
                rotation_axis='FH',
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
    
# Compute the projected rotation based on the scan that the item is being rotated on
def compute_projected_rotation(
    angle_diff_deg, RLAngle_deg, APAngle_deg, FHAngle_deg, rotation_axis
    ):
    # Convert all angles to radians
    angle_diff_rad = math.radians(angle_diff_deg)
    RLAngle_rad = math.radians(RLAngle_deg)
    APAngle_rad = math.radians(APAngle_deg)
    FHAngle_rad = math.radians(FHAngle_deg)

    # Compute the rotation matrices around each axis
    R_RL = rotation_matrix_x(RLAngle_rad)
    R_AP = rotation_matrix_y(APAngle_rad)
    R_FH = rotation_matrix_z(FHAngle_rad)

    # Compute the overall original rotation matrix
    R_original =np.linalg.multi_dot(
            [R_FH, R_AP, R_RL]
        )

    # Compute the rotation matrix for the angle difference around the rotation axis, matrix before projection
    R_diff = get_rotation_matrix(rotation_axis, angle_diff_rad)

    # Compute the new rotation matrix after the projection
    R_new = np.linalg.multi_dot([R_original, R_diff])
    R_incremental = np.linalg.multi_dot([R_new, np.linalg.inv(R_original)])

    # Extract rotation angles around all three axes
    incremental_angles_rad = rotation_matrix_to_euler_angles(R_incremental)

    # Convert to degrees
    incremental_angles_deg = np.degrees(incremental_angles_rad)

    return incremental_angles_deg  # Array with [RL_angle, AP_angle, FH_angle]
    
# Create rotation matrices for each plane
def rotation_matrix_x(angle_rad):
        c = np.cos(angle_rad)
        s = np.sin(angle_rad)
        return np.array([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c],
        ])

def rotation_matrix_y(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c],
    ])

def rotation_matrix_z(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1],
    ])

def get_rotation_matrix(axis, angle_rad):
    if axis == "RL":
        return rotation_matrix_x(angle_rad)
    elif axis == "AP":
        return rotation_matrix_y(angle_rad)
    elif axis == "FH":
        return rotation_matrix_z(angle_rad)
    else:
        raise ValueError(f"Unknown rotation axis: {axis}")

def extract_rotation_angle(R, axis):
    if axis == "RL":
        # Rotation around X-axis
        angle_rad = np.arctan2(R[2, 1], R[2, 2])
    elif axis == "AP":
        # Rotation around Y-axis
        angle_rad = np.arctan2(-R[2, 0], np.sqrt(R[0, 0]**2 + R[1, 0]**2))
    elif axis == "FH":
        # Rotation around Z-axis
        angle_rad = np.arctan2(R[1, 0], R[0, 0])
    else:
        raise ValueError(f"Unknown rotation axis: {axis}")
    return angle_rad

# Obtain seperate rotations as angles from the matrix to be sent as an event to the parameter checker
def rotation_matrix_to_euler_angles(R):
    """
    Extract Euler angles (rotations around x, y, z axes) from a rotation matrix.
    The rotation matrix should represent rotations in the order R = Rz * Ry * Rx.
    """
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        x_angle = np.arctan2(R[2, 1], R[2, 2])
        y_angle = np.arctan2(-R[2, 0], sy)
        z_angle = np.arctan2(R[1, 0], R[0, 0])
    else:
        x_angle = np.arctan2(-R[1, 2], R[1, 1])
        y_angle = np.arctan2(-R[2, 0], sy)
        z_angle = 0

    return np.array([x_angle, y_angle, z_angle])  # [RL_angle, AP_angle, FH_angle]
