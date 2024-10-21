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
    QLinearGradient,
)
from PyQt6.QtWidgets import (
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
    QApplication,
)

from typing import List, Optional
from events import EventEnum
from keys import Keys
from simulator.scanlist import AcquiredSeries, AcquiredImage, ScanVolume
from utils.logger import log
from views.items.custom_polygon_item import CustomPolygonItem
from views.items.measurement_tool import MeasurementTool
from views.items.middle_line_item import MiddleLineItem
from views.items.stacks_item import SlicecItem
from views.items.zoomin import ZoomableView
from views.items.stacks_item import SlicecItem
from views.ui.scanlist_ui import ScanlistListWidget


class AcquiredSeriesViewer2D(ZoomableView):
    stackSignal = pyqtSignal(int)
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
        # self.scan_volume = None
        self.scan_volumes: List[ScanVolume] = []

        # STACKS
        # Set active stack index to 0
        self.selected_stack_indx = 0
        self.stacks: List[StackItem] = []

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
        self.slices_display = []

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
        self.export_image_with_dicomdir_action = QAction(
            "Export image with DICOMDIR..."
        )
        self.right_click_menu.addAction(self.export_image_with_dicomdir_action)

        self.export_series_with_dicomdir_action = QAction(
            "Export series with DICOMDIR..."
        )
        self.right_click_menu.addAction(self.export_series_with_dicomdir_action)

        self.export_examination_with_dicomdir_action = QAction(
            "Export examination with DICOMDIR..."
        )
        self.right_click_menu.addAction(self.export_examination_with_dicomdir_action)

        self.scene.installEventFilter(self)

        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(QPen(QColor(255, 0, 0), 2))
        self.scene.addItem(self.line_item)

        self.text_item = QGraphicsTextItem()
        self.text_item.setDefaultTextColor(QColor(255, 165, 0))
        self.scene.addItem(self.text_item)

        self.measure = MeasurementTool(self.line_item, self.text_item, self)

        self.only_display_image = False
        self.view_only_instance = False

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
    # TODO: get current active stack scan volume display
    def eventFilter(self, source, event):
        # If this instance is only for displaying images, do not allow any interaction with the CustomPolygonItem
        # instead, the events are passed to the ZoomableView to enable measurements and zooming mouse events etc.
        if self.view_only_instance:
            return super().eventFilter(source, event)

        # if self.get_stack_for_stack_id(self.selected_stack_indx) == None:
        #     # print("HEREEE")
        #     super().eventFilter(source, event)
        #     return True

        if (
            event.type() == QEvent.Type.GraphicsSceneMouseMove
            and self.get_stack_for_stack_id(self.selected_stack_indx) is not None
        ):
            # check if the stack is non
            # if self.get_stack_for_stack_id(self.selected_stack_indx) is None:
            #     return RuntimeError("No stack found for selected stack index")
            # if self.scan_volume_display and self.scan_volume_display.is_rotating:
            if (
                self.get_stack_for_stack_id(self.selected_stack_indx).volume_display
                and self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.is_rotating
            ):
                # self.scan_volume_display.handle_scene_mouse_move(event)
                self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.handle_scene_mouse_move(event)
                return True

            if (
                self.get_stack_for_stack_id(self.selected_stack_indx).volume_display
                is not None
                and self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.is_being_scaled
            ):
                self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.scale_handle_move_event_handler(event)
                return True
        elif (
            event.type() == QEvent.Type.GraphicsSceneMouseRelease
            and self.get_stack_for_stack_id(self.selected_stack_indx) is not None
        ):
            # if self.scan_volume_display and self.scan_volume_display.is_rotating:
            if (
                self.get_stack_for_stack_id(self.selected_stack_indx).volume_display
                and self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.is_rotating
            ):
                # self.scan_volume_display.handle_scene_mouse_release(event)
                self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.handle_scene_mouse_release(event)
            # if (
            #     self.scan_volume_display is not None
            #     and self.scan_volume_display.is_being_scaled
            # ):
            if (
                self.get_stack_for_stack_id(self.selected_stack_indx).volume_display
                is not None
                and self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.is_being_scaled
            ):
                self.get_stack_for_stack_id(
                    self.selected_stack_indx
                ).volume_display.scale_handle_release_event_handler()
                return True
        return super().eventFilter(source, event)

    def get_stack_for_stack_id(self, stack_index):
        # print("STACKS " + str(self.stacks))
        for stack in self.stacks:
            if stack.stack_index == stack_index:
                return stack

        return None

    def get_scan_volume_for_stack_index(self, stack_index):
        for vol in self.scan_volumes:
            if vol.stack_index == stack_index:
                return vol

        return None

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

    def position_color_scale_elements(self):
        """Ensure the color scale and labels are positioned correctly."""
        padding = 20

        self.color_scale_label.move(
            padding, self.height() // 2 - self.color_scale_label.height() // 2
        )

        self.min_value_label.move(
            self.color_scale_label.x() + self.color_scale_label.width() + 5,
            self.color_scale_label.y() - 5,
        )
        self.mid_value_label.move(
            self.color_scale_label.x() + self.color_scale_label.width() + 5,
            self.color_scale_label.y() + self.color_scale_label.height() // 2 - 10,
        )
        self.max_value_label.move(
            self.color_scale_label.x() + self.color_scale_label.width() + 5,
            self.color_scale_label.y() + self.color_scale_label.height() - 20,
        )

        self.min_value_label.adjustSize()
        self.mid_value_label.adjustSize()
        self.max_value_label.adjustSize()

    def _displayArray(self, window_center=None, window_width=None):
        if self.array is None:
            return

        if self.array is not None:
            array_norm = (self.array[:, :] - np.min(self.array)) / (
                np.max(self.array) - np.min(self.array)
            )
            array_8bit = (array_norm * 255).astype(np.uint8)

            if window_center is None or window_width is None:
                window_center = np.mean(self.array)
                window_width = np.max(self.array) - np.min(self.array)

            min_window = window_center - (window_width / 2)
            max_window = window_center + (window_width / 2)

            array_clamped = np.clip(self.array, min_window, max_window)
            array_norm = (array_clamped - min_window) / (max_window - min_window)
            array_8bit = (array_norm * 255).astype(np.uint8)

            # Create QImage and display
            image = np.ascontiguousarray(array_8bit)
            height, width = image.shape
            qimage = QImage(
                image.data, width, height, width, QImage.Format.Format_Grayscale8
            )

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.pixmap_item.setPos(0, 0)
            self.scene.setSceneRect(0, 0, width, height)
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

    # TODO: call methods on current active stack index scan volume instead
    def update(self, event: EventEnum, **kwargs):
        if event == EventEnum.SCAN_VOLUME_CHANGED:
            # self.scan_volume.clamp_to_scanner_dimensions()
            # self._update_scan_volume_display()
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).clamp_to_scanner_dimensions()
            self._update_scan_volume_display(
                self.get_stack_for_stack_id(self.selected_stack_indx)
            )
            # self.viewport().update()
            # QApplication.processEvents()

        if event == EventEnum.SCAN_VOLUME_DISPLAY_TRANSLATED:
            # self.scan_volume.remove_observer(self)
            # self.scan_volume.translate_scan_volume(
            #     kwargs[Keys.SCAN_VOLUME_DIRECTION_VECTOR_IN_COORDS.value]
            # )
            # self.scan_volume.add_observer(self)
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).remove_observer(self)
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).translate_scan_volume(
                kwargs[Keys.SCAN_VOLUME_DIRECTION_VECTOR_IN_COORDS.value]
            )
            self.get_scan_volume_for_stack_index(self.selected_stack_indx).add_observer(
                self
            )
        elif event == EventEnum.SCAN_VOLUME_DISPLAY_ROTATED:
            rotation_angle_deg = kwargs["rotation_angle_deg"]
            rotation_axis = kwargs["rotation_axis"]
            rotation_angle_rad = np.deg2rad(rotation_angle_deg)
            # self.scan_volume.remove_observer(self)
            # self.scan_volume.rotate_scan_volume(rotation_angle_rad, rotation_axis)
            # self.scan_volume.add_observer(self)
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).remove_observer(self)
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).rotate_scan_volume(rotation_angle_rad, rotation_axis)
            self.get_scan_volume_for_stack_index(self.selected_stack_indx).add_observer(
                self
            )

        elif event == EventEnum.SCAN_VOLUME_DISPLAY_SCALED:
            scale_factor_x = kwargs["scale_factor_x"]
            scale_factor_y = kwargs["scale_factor_y"]
            origin_plane = kwargs["origin_plane"]
            handle_pos = kwargs["handle_pos"]
            center_pos = kwargs["center_pos"]

            # self.scan_volume.remove_observer(self)
            # self.scan_volume.scale_scan_volume(
            #     scale_factor_x, scale_factor_y, origin_plane, handle_pos, center_pos
            # )
            # self._update_scan_volume_display()
            # self.scan_volume.add_observer(self)
            self.get_scan_volume_for_stack_index(
                self.selected_stack_indx
            ).scale_scan_volume(
                scale_factor_x, scale_factor_y, origin_plane, handle_pos, center_pos
            )
            self._update_scan_volume_display(
                self.get_stack_for_stack_id(self.selected_stack_indx)
            )

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

    def setAcquiredSeries(self, acquired_series: AcquiredSeries, completed_scan=False):
        if acquired_series is not None:
            self.acquired_series = acquired_series
            self.displayed_image_index = 0
            self.update_buttons_visibility()

            # TODO: is this all code in if condition needed
            if len(self.stacks) == 0:
                self.scan_volumes = []
                new_stack = StackItem(self.pixmap_item, self, 0)
                new_scan_vol = ScanVolume(0)
                self.scan_volumes.append(new_scan_vol)
                new_stack.volume_display.setScanVolume(new_scan_vol)
                self.stacks.append(new_stack)

            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
                completed_scan,
            )
        else:
            self.acquired_series = None
            self.setDisplayedImage(None)

    def setScanCompleteAcquiredData(self, acquired_series: AcquiredSeries):
        if len(self.stacks) == 0:
            self.scan_volumes = []
            new_stack = StackItem(self.pixmap_item, self, 0)
            new_scan_vol = ScanVolume(0)
            self.scan_volumes.append(new_scan_vol)
            new_stack.volume_display.setScanVolume(new_scan_vol)
            self.stacks.append(new_stack)

        self.setAcquiredSeries(acquired_series)
        self.only_display_image = True

    def setDisplayedImage(
        self,
        image: AcquiredImage,
        scan_plane="Unknown",
        series_name="Scan",
        completed=False,
    ):
        previous_scan_plane = None
        if image is not None:
            previous_scan_plane = image.image_geometry.plane
        self.displayed_image = image
        if image is not None:
            self.array = image.image_data

            # if stack changed, then also update active states of visual elements of scan volumes of different stacks
            # if image.stack_index != self.selected_stack_indx:
            #     self.stackSignal.emit(image.stack_index)
            #     self.update_stacks_active_state(image.stack_index)

            # self.scan_volume_display.set_displayed_image(image)
            # TODO: set scan volume display image of current active stack instead
            self.get_stack_for_stack_id(
                self.selected_stack_indx
            ).volume_display.set_displayed_image(image)

            # Set default window and level values
            self.window_center = np.mean(self.array)
            self.window_width = np.max(self.array) - np.min(self.array)

            self.scan_volume_display.set_displayed_image(image)

            # Determine the scan plane
            icon_path = f"resources/icons/plane_orientation/{image.image_geometry.plane.lower()}.svg"
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

        self._displayArray(self.window_center, self.window_width)
        if (
            self.only_display_image != True
            and self.displayed_image is not None
            and completed is not True
        ):
            self._update_scan_volume_display(
                self.get_stack_for_stack_id(self.selected_stack_indx)
            )
            # if scan plane of new image is different, then we need to update also all stacks
            # if previous_scan_plane != self.displayed_image.image_geometry.plane:
            #     self.update_all_stack_displays()

    def update_all_stack_displays(self):
        for s in self.stacks:
            self._update_scan_volume_display(s)

    def update_stacks_active_state(self, active_index):
        for s in self.stacks:
            if s.stack_index == active_index:
                s.set_active_settings()
            else:
                s.set_inactive_settings()

    def change_stack(self, stack_index):
        self.selected_stack_indx = stack_index
        self.update_stacks_active_state(stack_index)
        self.update_all_stack_displays()

    def delete_stack(self, stack_index):
        # delete stacks corresponding to stack index
        stack_itm_indices_to_delete = []
        for inx, stack in enumerate(self.stacks):
            if stack.stack_index == stack_index:
                stack_itm_indices_to_delete.append(inx)
        for inx in stack_itm_indices_to_delete:
            del self.stacks[inx]
        # delete scan volumes corresponding to stack index
        vol_itm_indices_to_delete = []
        for inx, vol in enumerate(self.scan_volumes):
            if vol.stack_index == stack_index:
                vol_itm_indices_to_delete.append(inx)
        for inx in vol_itm_indices_to_delete:
            del self.scan_volumes[inx]

    def setScanVolumes(self, scan_volumes: List[ScanVolume]):
        if len(self.scan_volumes) > 0:
            # remove observers from current scan volumes as changes shouldn't be emitted anymore from these volumes
            for scan_vol in self.scan_volumes:
                scan_vol.remove_observer(self)
        # IMPORTANT: need to set both stacks and scan volumes arrays to empty lists as scan item was switched
        self.scan_volumes = []
        # I hope Python's automatic garbage collection destroys previous stack items that were in the list if we set list to empty list
        # as we don't want previous stack items anymore
        self.stacks = []

        # add observers to each scan volume
        for scan_vol in scan_volumes:
            scan_vol.add_observer(self)
            self.scan_volumes.append(scan_vol)
            # new stack object for each volume
            stack = StackItem(self.pixmap_item, self, scan_vol.stack_index)
            stack.volume_display.set_scan_volume(scan_vol)
            self.stacks.append(stack)

        # TODO: make this take actually the selected index of scan item to set active states
        inx = 0
        for stack in self.stacks:
            # TODO: self.selected_stack_indx must be set to 0 after selecting active scan item
            if stack.stack_index == self.selected_stack_indx:
                stack.set_active_settings()
            else:
                stack.set_inactive_settings()
            inx += 1
            self._update_scan_volume_display(stack)

    # TODO: clean current scan volumes and initialize new array of scan volumes of ScanItem and also create StackItems for each scan volume and
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

    def _update_scan_volume_display_for_active_stack_item(self):
        self._update_scan_volume_display(
            self.get_stack_for_stack_id(self.selected_stack_indx)
        )

    def _update_scan_volume_display(self, stack_item: "StackItem"):
        # TODO: call these methods on StackItem instead
        """Updates the intersection polygon between the scan volume and the displayed image."""
        # if self.displayed_image is not None and self.scan_volume is not None:
        #     (
        #         intersection_volume_edges_in_pixmap_coords,
        #         intersection_middle_edges_in_pixamp_coords,
        #         intersection_slice_edges_in_pixamp_coords,
        #     ) = self.scan_volume.compute_intersection_with_acquired_image(
        #         self.displayed_image
        #     )
        #     self.scan_volume_display.setPolygonFromPixmapCoords(
        #         intersection_volume_edges_in_pixmap_coords
        #     )
        #     self.middle_lines_display.setPolygonFromPixmapCoords(
        #         intersection_middle_edges_in_pixamp_coords
        #     )
        #     for stack in self.slices_display:
        #         stack.setPolygon(QPolygonF())
        #     self.slices_display = []
        #     for slice_edges in intersection_slice_edges_in_pixamp_coords:
        #         slice_item = SlicecItem(self.pixmap_item)
        #         slice_item.setPolygonFromPixmapCoords(slice_edges)
        #         self.slices_display.append(slice_item)
        #         # self.stacks_display.setPolygonFromPixmapCoords(intersection_slice_edges_in_pixamp_coords)
        # else:
        #     self.scan_volume_display.setPolygon(QPolygonF())
        #     self.middle_lines_display.setPolygon(QPolygonF())
        #     # self.stacks_display.setPolygon(QPolygonF())
        #     for stack in self.slices_display:
        #         stack.setPolygon(QPolygonF())
        #     self.slices_display = []
        # self.scan_volume_display.update_slice_lines()
        if self.displayed_image is not None and stack_item is not None:
            # scan_item_volume = None
            # for vol in self.scan_volumes:
            #     if vol.stack_index == stack_item.stack_index:
            #         scan_item_volume = vol
            scan_item_volume = self.get_scan_volume_for_stack_index(
                stack_item.stack_index
            )
            (
                intersection_volume_edges_in_pixmap_coords,
                intersection_middle_edges_in_pixamp_coords,
                intersection_slice_edges_in_pixamp_coords,
            ) = scan_item_volume.compute_intersection_with_acquired_image(
                self.displayed_image
            )
            stack_item.update_objects_with_pixmap_coords(
                intersection_volume_edges_in_pixmap_coords,
                intersection_middle_edges_in_pixamp_coords,
                intersection_slice_edges_in_pixamp_coords,
            )
        else:
            if stack_item is not None:
                stack_item.clear_objects()

    def contextMenuEvent(self, event):
        """Event handler for if the user requests to open the right-click context menu."""

        super().contextMenuEvent(event)

        # Enable the export actions only if we have at least one displayed image that can be exported,
        # in the window that was right-clicked on.
        if self.displayed_image is not None:
            self.export_action.setEnabled(True)
            self.export_image_with_dicomdir_action.setEnabled(True)
            self.export_series_with_dicomdir_action.setEnabled(True)
            self.export_examination_with_dicomdir_action.setEnabled(True)
        else:
            self.export_action.setEnabled(False)
            self.export_image_with_dicomdir_action.setEnabled(False)
            self.export_series_with_dicomdir_action.setEnabled(False)
            self.export_examination_with_dicomdir_action.setEnabled(False)

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


class StackItem:
    volume_display: Optional[CustomPolygonItem] = None
    middle_line_display: Optional[MiddleLineItem] = None
    slices_display: List[SlicecItem] = []
    activ_stack = False
    stack_index = 0

    def __init__(self, pixmap_item, series_viewer, stack_index):
        self.pixmap_item = pixmap_item
        self.series_viewer = series_viewer
        self.volume_display = CustomPolygonItem(pixmap_item, series_viewer)
        # TODO: I think need to add viewer as observer for volume display as well
        self.volume_display.add_observer(series_viewer)
        self.volume_display.set_color(Qt.GlobalColor.red)
        self.volume_display.set_movability(False)
        self.middle_line_display = MiddleLineItem(pixmap_item)
        self.stack_index = stack_index
        self.volume_display.middle_point.setPen(Qt.GlobalColor.red)

    # clear all the visual elements connected to this stack before removing this stack item
    def __del__(self):
        self.clear_objects()

    # show this scan volume in yellow as selected scan volume and hide slices and middle lines, make it movable
    def set_active_settings(self):
        self.activ_stack = True
        self.volume_display.set_color(Qt.GlobalColor.yellow)
        self.volume_display.set_movability(True)
        self.middle_line_display.setVisible(True)
        self.volume_display.set_handles_visible()
        self.volume_display.is_active_stack = True
        self.volume_display.middle_point.setPen(Qt.GlobalColor.yellow)

    # unselect this scan volume so set it red and make non-movable
    def set_inactive_settings(self):
        self.activ_stack = False
        self.volume_display.set_color(Qt.GlobalColor.red)
        self.volume_display.set_movability(False)
        self.middle_line_display.setPolygon(QPolygonF())
        self.middle_line_display.setVisible(False)
        # self.stacks_display.setPolygon(QPolygonF())
        for slice in self.slices_display:
            slice.setPolygon(QPolygonF())
        self.slices_display = []
        self.volume_display.set_handles_invisible()
        self.volume_display.is_active_stack = False
        self.volume_display.middle_point.setPen(Qt.GlobalColor.red)

    # update stack item display component with coordinates
    def update_objects_with_pixmap_coords(
        self, volume_edges, middle_edges, slice_edges
    ):
        self.volume_display.setPolygon(QPolygonF())

        self.volume_display.setPolygonFromPixmapCoords(volume_edges)
        self.middle_line_display.setPolygonFromPixmapCoords(middle_edges)
        for slice in self.slices_display:
            slice.setPolygon(QPolygonF())
        self.slices_display = []
        if self.activ_stack:
            for slice_edges in slice_edges:
                slice_item = SlicecItem(self.pixmap_item)
                slice_item.setPolygonFromPixmapCoords(slice_edges)
                self.slices_display.append(slice_item)

        # TODO: try to update viewer here, it sometimes happens that polygon is set with coordinates, but views are not updated
        self.series_viewer.viewport().update()
        # QApplication.processEvents()

    # clear all objects for this stack item
    def clear_objects(self):
        self.volume_display.setPolygon(QPolygonF())
        self.middle_line_display.setPolygon(QPolygonF())
        # self.stacks_display.setPolygon(QPolygonF())
        for slice in self.slices_display:
            slice.setPolygon(QPolygonF())
        self.slices_display = []
