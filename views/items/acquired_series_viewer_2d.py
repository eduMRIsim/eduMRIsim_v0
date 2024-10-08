import numpy as np
from PyQt6.QtCore import Qt, QEvent, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QAction,
    QPen,
    QResizeEvent,
    QImage,
    QPixmap,
    QPolygonF,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QMouseEvent,
    QKeyEvent,
    QCursor
)
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSizePolicy,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMenu,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsOpacityEffect,
)

from events import EventEnum
from keys import Keys
from simulator.scanlist import AcquiredSeries, ScanVolume
from utils.logger import log
from views.items.measurement_tool import MeasurementTool
from views.items.custom_polygon_item import CustomPolygonItem
from views.items.stacks_item import StacksItem
from views.ui.scanlist_ui import ScanlistListWidget
from views.items.middle_line_item import MiddleLineItem


class AcquiredSeriesViewer2D(QGraphicsView):
    """Displays an acquired series of 2D images in a QGraphicsView. The user can scroll through the images using the mouse wheel. The viewer also displays the intersection of the scan volume with the image in the viewer. The intersection is represented with a CustomPolygonItem. The CustomPolygonItem is movable and sends geometry changes to the observers. Each acquired image observes the CustomPolygonItem and updates the scan volume when the CustomPolygonItem is moved."""

    def __init__(self):
        super().__init__()

        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually.
        self.scene = QGraphicsScene(self)

        # Creates a pixmap graphics item that will be added to the scene
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # Sets the created scene as the scene for the graphics view
        self.setScene(self.scene)

        # Sets the render hint to enable antialiasing, which makes the image look smoother. Aliasings occur when a high-resolution image is displayed or rendered at a lower resolution, leading to the loss of information and the appearance of stair-stepped edges. Antialiasing techniques smooth out these jagged edges by introducing intermediate colors or shades along the edges of objects.
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Set the background color to black
        self.setBackgroundBrush(QColor(0, 0, 0))  # RGB values for black

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Initialize displayed image to None
        self.displayed_image = None

        # Initalize displayed series to None
        self.acquired_series = None

        # Initalize scan volume to None
        self.scan_volume = None

        # Initialize array attribute to None
        self.array = None

        # Scroll amount value used for scrolling sensitivity
        self.scroll_amount = 0

        self.scan_volume_display = CustomPolygonItem(
            self.pixmap_item, self
        )  # Create a custom polygon item that is a child of the pixmap item

        self.middle_lines_display = MiddleLineItem(
            self.pixmap_item
        )  # adds middle lines of current scan volume
        # self.stacks_display = StacksItem(self.pixmap_item)
        self.stacks_displays = []

        self.scan_volume_display.add_observer(self)

        #  Display scan plane label
        self.scan_plane_label = QLabel(self)
        self.scan_plane_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.scan_plane_label.setStyleSheet("padding: 5px;")
        self.scan_plane_label.resize(100, 100)
        self.scan_plane_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.updateLabelPosition()

        # Display scan name
        self.series_name_label = QLabel(self)
        self.series_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.series_name_label.setStyleSheet(
            "color: white; font-size: 14px; padding: 5px;"
        )
        self.series_name_label.resize(200, 50)
        self.series_name_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.series_name_label.move(0, 0)

        # Up and down buttons
        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")
        self.up_button.setFixedSize(30, 30)
        self.down_button.setFixedSize(30, 30)
        self.up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.down_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.setSpacing(8)
        button_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.up_button.clicked.connect(self.go_up)
        self.down_button.clicked.connect(self.go_down)
        self.setLayout(button_layout)
        self.update_buttons_visibility()

        # Right-click context menu
        # The trigger for export_action is set in main_ctrl.py, ui_signals() and handle_viewingPortExport_triggered()
        self.right_click_menu = QMenu(self)
        self.export_action = QAction("Export...")
        self.right_click_menu.addAction(self.export_action)

        self.scene.installEventFilter(self)

        # Zoom controls
        self.zooming_enabled = False
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.zoom_sensitivity = 0.005
        self.max_zoom_out = 0.5
        self.max_zoom_in = 10
        self.zoom_factor = None


        # Key press controls
        self.zoom_key_pressed = False
        self.measuring_key_pressed = False

        # Measurement tool
        self.measuring_enabled = False

        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(QPen(QColor(255, 0, 0), 2))
        self.scene.addItem(self.line_item)

        self.text_item = QGraphicsTextItem()
        self.text_item.setDefaultTextColor(QColor(255, 0, 0))
        self.scene.addItem(self.text_item)

        self.measure = MeasurementTool(self.line_item, self.text_item, self)

    # Mouse press for zooming/measuring
    def mousePressEvent(self, event: QMouseEvent):
        if self.zooming_enabled and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.mouse_pressed = True
                self.last_mouse_pos = event.pos()
        if self.measuring_enabled:
            self.measure.start_measurement(self.mapToScene(event.pos()))
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.zooming_enabled and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.mouse_pressed = False
                self.last_mouse_pos = None
        elif self.measure.is_measuring:
            self.measure.end_measurement()
        else:
            super().mouseReleaseEvent(event)

    # Key press for zooming/measuring
    def keyPressEvent(self, event: QKeyEvent):
        if self.zooming_enabled and not self.measuring_enabled and event.key() == Qt.Key.Key_Z:
                self.zoom_key_pressed = True
        elif event.key() == Qt.Key.Key_M and self.measure.is_measuring:
                self.measure.end_measurement()
        elif event.key() == Qt.Key.Key_M and not self.measure.is_measuring:
                cursor_pos = QCursor.pos()
                scene_pos = self.mapToScene(self.mapFromGlobal(cursor_pos))
                self.measure.start_measurement(scene_pos)
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        if self.zooming_enabled and self.measuring_enabled == False and event.key() == Qt.Key.Key_Z:
                self.zoom_key_pressed = False
        if event.key() == Qt.Key.Key_M:
                self.measuring_key_pressed = False
        else:
            super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # handle zoom
        if self.zooming_enabled and not self.measuring_enabled and self.zoom_key_pressed :
            if self.mouse_pressed and self.last_mouse_pos is not None:
                current_pos = event.pos()

                delta_y = current_pos.y() - self.last_mouse_pos.y()

                self.zoom_factor = 1 + (delta_y * self.zoom_sensitivity)

                current_zoom = self.transform().m11()

                new_zoom = current_zoom * self.zoom_factor

                if self.max_zoom_out <= new_zoom <= self.max_zoom_in:
                    self.scale(self.zoom_factor, self.zoom_factor)

                self.last_mouse_pos = current_pos
        # handle measuring tool
        elif self.measure.is_measuring:
            self.measure.update_measurement(self.mapToScene(event.pos()))
        else:
            super().mouseMoveEvent(event)

    def zoom_in(self, center_point):
        if self.transform().m11() < self.max_zoom_in:
            self.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self, center_point):
        if self.transform().m11() > self.max_zoom_out:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            self.centerOn(center_point)

    def update_buttons_visibility(self):
        if self.acquired_series is None:
            self.up_button.hide()
            self.down_button.hide()
        else:
            self.up_button.show()
            self.down_button.show()

            # Reduce opacity of up button when on the first image
            if self.displayed_image_index == 0:
                self.up_button.setEnabled(False)
                self.set_button_opacity(self.up_button, 0.8)
            else:
                self.up_button.setEnabled(True)
                self.set_button_opacity(self.up_button, 1.0)

            # Reduce opacity of down button when on the last image
            if (
                self.displayed_image_index
                == len(self.acquired_series.list_acquired_images) - 1
            ):
                self.down_button.setEnabled(False)
                self.set_button_opacity(self.down_button, 0.8)
            else:
                self.down_button.setEnabled(True)
                self.set_button_opacity(self.down_button, 1.0)

    def set_button_opacity(self, button, opacity_value):
        opacity_effect = QGraphicsOpacityEffect(button)
        opacity_effect.setOpacity(opacity_value)
        button.setGraphicsEffect(opacity_effect)

    # up button functionality
    def go_up(self):
        if self.acquired_series is None:
            return
        if self.displayed_image_index > 0:
            self.displayed_image_index -= 1
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        self.update_buttons_visibility()

    # down button functionality
    def go_down(self):
        if self.acquired_series is None:
            return
        if (
            self.displayed_image_index
            < len(self.acquired_series.list_acquired_images) - 1
        ):
            self.displayed_image_index += 1
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        self.update_buttons_visibility()

    # Eventfilter used for Rotation. Making the rotation handlers moveable with mouse move events did not work well
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.GraphicsSceneMouseMove:
            if self.scan_volume_display and self.scan_volume_display.is_rotating:
                self.scan_volume_display.handle_scene_mouse_move(event)
                return True
            if (
                self.scan_volume_display is not None
                and self.scan_volume_display.is_being_scaled
            ):
                self.scan_volume_display.scale_handle_move_event_handler(event)
                return True
        elif event.type() == QEvent.Type.GraphicsSceneMouseRelease:
            if self.scan_volume_display and self.scan_volume_display.is_rotating:
                self.scan_volume_display.handle_scene_mouse_release(event)
            if (
                self.scan_volume_display is not None
                and self.scan_volume_display.is_being_scaled
            ):
                self.scan_volume_display.scale_handle_release_event_handler()
                return True
        return super().eventFilter(source, event)

    def resizeEvent(self, event: QResizeEvent):
        """This method is called whenever the graphics view is resized. It ensures that the image is always scaled to fit the view."""
        super().resizeEvent(event)

        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.updateLabelPosition()

    def updateLabelPosition(self):
        if self.scan_plane_label.pixmap() is not None:
            label_width = self.scan_plane_label.pixmap().width()
            label_height = self.scan_plane_label.pixmap().height()
        else:
            label_width = 0
            label_height = 0

        padding = 10
        x_pos = self.width() - label_width - padding
        y_pos = self.height() - label_height - padding
        self.scan_plane_label.move(x_pos, y_pos)
        self.scan_plane_label.adjustSize()
        self.scan_plane_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

    def _displayArray(self):
        width, height = 0, 0
        if self.array is not None:

            # Normalize the slice values for display
            array_norm = (self.array[:, :] - np.min(self.array)) / (
                np.max(self.array) - np.min(self.array)
            )
            array_8bit = (array_norm * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(
                image.data, width, height, width, QImage.Format.Format_Grayscale8
            )

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.pixmap_item.setPos(0, 0)  # Ensure the pixmap item is at (0, 0)
            self.scene.setSceneRect(
                0, 0, width, height
            )  # Adjust the scene rectangle to match the pixmap dimensions

        else:
            # Set a black image when self.array is None
            black_image = QImage(1, 1, QImage.Format.Format_Grayscale8)
            black_image.fill(Qt.GlobalColor.black)
            pixmap = QPixmap.fromImage(black_image)
            self.pixmap_item.setPixmap(pixmap)
            self.scene.setSceneRect(0, 0, 1, 1)

        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)

    def handle_calculate_direction_vector_from_move_event(
        self, direction_vector_in_pixmap_coords: QPointF
    ) -> np.array:
        parsed_direction_vector_in_pixmap_coords = (
            direction_vector_in_pixmap_coords.x(),
            direction_vector_in_pixmap_coords.y(),
        )
        direction_vector_in_LPS_coords = np.array(
            self.displayed_image.image_geometry.pixmap_coords_to_LPS_coords(
                parsed_direction_vector_in_pixmap_coords
            )
        ) - np.array(
            self.displayed_image.image_geometry.pixmap_coords_to_LPS_coords((0, 0))
        )

        return direction_vector_in_LPS_coords

    def update(self, event: EventEnum, **kwargs):
        if event == EventEnum.SCAN_VOLUME_CHANGED:
            self.scan_volume.clamp_to_scanner_dimensions()
            self._update_scan_volume_display()

        if event == EventEnum.SCAN_VOLUME_DISPLAY_TRANSLATED:
            self.scan_volume.remove_observer(self)
            self.scan_volume.translate_scan_volume(
                kwargs[Keys.SCAN_VOLUME_DIRECTION_VECTOR_IN_COORDS.value]
            )
            self.scan_volume.add_observer(self)
        elif event == EventEnum.SCAN_VOLUME_DISPLAY_ROTATED:
            rotation_angle_deg = kwargs["rotation_angle_deg"]
            rotation_axis = kwargs["rotation_axis"]
            rotation_angle_rad = np.deg2rad(rotation_angle_deg)
            self.scan_volume.remove_observer(self)
            self.scan_volume.rotate_scan_volume(rotation_angle_rad, rotation_axis)
            self.scan_volume.add_observer(self)
        elif event == EventEnum.SCAN_VOLUME_DISPLAY_SCALED:
            scale_factor_x = kwargs["scale_factor_x"]
            scale_factor_y = kwargs["scale_factor_y"]
            origin_plane = kwargs["origin_plane"]
            handle_pos = kwargs["handle_pos"]
            center_pos = kwargs["center_pos"]

            # self.scan_volume.remove_observer(self)
            self.scan_volume.scale_scan_volume(
                scale_factor_x, scale_factor_y, origin_plane, handle_pos, center_pos
            )
            self._update_scan_volume_display()
            # self.scan_volume.add_observer(self)

    def wheelEvent(self, event):
        # Check if the array is None
        if self.array is None:
            # Do nothing and return
            return
        delta = event.angleDelta().y()
        self.scroll_amount += delta
        scroll_threshold = 120

        if self.scroll_amount <= -scroll_threshold:
            self.scroll_amount = 0
            new_displayed_image_index = min(
                self.displayed_image_index + 1,
                len(self.acquired_series.list_acquired_images) - 1,
            )
            self.displayed_image_index = new_displayed_image_index
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
            self.update_buttons_visibility()
        elif self.scroll_amount >= scroll_threshold:
            self.scroll_amount = 0
            new_displayed_image_index = max(self.displayed_image_index - 1, 0)
            self.displayed_image_index = new_displayed_image_index
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
            self.update_buttons_visibility()

    def setAcquiredSeries(self, acquired_series: AcquiredSeries):
        if acquired_series is not None:
            self.acquired_series = acquired_series
            self.displayed_image_index = 0
            self.update_buttons_visibility()

            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        else:
            self.acquired_series = None
            self.setDisplayedImage(None)

    def setDisplayedImage(self, image, scan_plane="Unknown", series_name="Scan"):
        self.displayed_image = image
        if image is not None:
            self.array = image.image_data
            self.scan_volume_display.set_displayed_image(image)

            # Determine the scan plane
            icon_path = f"resources/icons/plane_orientation/{scan_plane.lower()}.svg"
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.scan_plane_label.setPixmap(scaled_pixmap)
            self.scan_plane_label.resize(scaled_pixmap.width(), scaled_pixmap.height())

            # Set the scan name
            scan_number = self.displayed_image_index + 1
            self.series_name_label.setText(f"{series_name} ({scan_number}) ")

            self.updateLabelPosition()
        else:
            self.array = None
            self.scan_plane_label.clear()
            self.series_name_label.setText("")

        self._displayArray()
        self._update_scan_volume_display()

    def setScanVolume(self, scan_volume: ScanVolume):
        # remove the observer from the previous scan volume
        if self.scan_volume is not None:
            self.scan_volume.remove_observer(self)
        # set the new scan volume and observe it
        self.scan_volume = scan_volume
        if self.scan_volume is not None:
            self.scan_volume.add_observer(self)
            self.scan_volume_display.set_scan_volume(scan_volume)
        else:
            self.scan_volume_display.set_scan_volume(None)
        self._update_scan_volume_display()

    def _update_scan_volume_display(self):
        """Updates the intersection polygon between the scan volume and the displayed image."""
        if self.displayed_image is not None and self.scan_volume is not None:
            (
                intersection_volume_edges_in_pixmap_coords,
                intersection_middle_edges_in_pixamp_coords,
                intersection_slice_edges_in_pixamp_coords,
            ) = self.scan_volume.compute_intersection_with_acquired_image(
                self.displayed_image
            )
            self.scan_volume_display.setPolygonFromPixmapCoords(
                intersection_volume_edges_in_pixmap_coords
            )
            self.middle_lines_display.setPolygonFromPixmapCoords(
                intersection_middle_edges_in_pixamp_coords
            )
            for stack in self.stacks_displays:
                stack.setPolygon(QPolygonF())
            self.stacks_displays = []
            for slice_edges in intersection_slice_edges_in_pixamp_coords:
                stack_item = StacksItem(self.pixmap_item)
                stack_item.setPolygonFromPixmapCoords(slice_edges)
                self.stacks_displays.append(stack_item)
                # self.stacks_display.setPolygonFromPixmapCoords(intersection_slice_edges_in_pixamp_coords)
        else:
            self.scan_volume_display.setPolygon(QPolygonF())
            self.middle_lines_display.setPolygon(QPolygonF())
            # self.stacks_display.setPolygon(QPolygonF())
            for stack in self.stacks_displays:
                stack.setPolygon(QPolygonF())
            self.stacks_displays = []
        # self.scan_volume_display.update_slice_lines()

    def contextMenuEvent(self, event):
        """Event handler for if the user requests to open the right-click context menu."""

        super().contextMenuEvent(event)

        # Enable the export button only if we have a displayed image that can be exported.
        if self.displayed_image is not None:
            self.export_action.setEnabled(True)
        else:
            self.export_action.setEnabled(False)

        # Execute and open the menu.
        action_performed = self.right_click_menu.exec(self.mapToGlobal(event.pos()))

        # If action_performed is None, the user didn't click on any action,
        # but instead they clicked outside the menu to close it.
        if action_performed is not None:
            log.info(f"{repr(action_performed.text())} action performed")
        else:
            log.info("No action performed")


class DropAcquiredSeriesViewer2D(AcquiredSeriesViewer2D):
    """Subclass of AcquiredSeriesViewer2D that can accept drops from scanlistListWidget. The dropEventSignal is emitted when a drop event occurs."""

    dropEventSignal = pyqtSignal(int)

    def __init__(self, ui):
        super().__init__()
        self.setAcceptDrops(True)
        self.zooming_enabled = False

        # This class requires a reference to the UI, since it needs to enable the viewport export buttons
        # when a scan item is dropped into it, so that the user can export it to a file.
        self.ui = ui

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        source_widget = event.source()
        # Should only accept drops if source widget is ScanlistListWidget and only one item is selected
        if (
            isinstance(source_widget, ScanlistListWidget)
            and len(source_widget.selectedIndexes()) == 1
        ):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        source_widget = event.source()
        selected_index = source_widget.selectedIndexes()[0].row()
        self.dropEventSignal.emit(selected_index)

        # Enable a viewing port export button only if the viewing port contains at least one image.
        if (
            self.ui.scanPlanningWindow1.acquired_series is not None
            and self.ui.scanPlanningWindow1.acquired_series.list_acquired_images
            is not None
        ):
            self.ui.scanPlanningWindow1ExportButton.setEnabled(True)
        if (
            self.ui.scanPlanningWindow2.acquired_series is not None
            and self.ui.scanPlanningWindow2.acquired_series.list_acquired_images
            is not None
        ):
            self.ui.scanPlanningWindow2ExportButton.setEnabled(True)
        if (
            self.ui.scanPlanningWindow3.acquired_series is not None
            and self.ui.scanPlanningWindow3.acquired_series.list_acquired_images
            is not None
        ):
            self.ui.scanPlanningWindow3ExportButton.setEnabled(True)

        event.accept()
