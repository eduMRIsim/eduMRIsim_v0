from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QCursor
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene

from utils.logger import log


class ZoomableView(QGraphicsView):
    zoomChanged = pyqtSignal(float)  # signals for zoom
    panChanged = pyqtSignal(int, int) # signals for panning 

    def __init__(self):
        super().__init__()
        # Initialize necessary variables
        self.window_width = None
        self.window_center = None
        self.scene = QGraphicsScene(self)

        self.mouse_pressed = False
        self.panning_mouse_pressed = False
        self.zoom_key_pressed = False
        self.panning_key_pressed = False
        self.measuring_key_pressed = False
        self.leveling_key_pressed = False  # For tracking if "L" is pressed
        self.last_mouse_pos = None
        self.zoom_sensitivity = 0.005
        self.measuring_enabled = False
        self.zooming_enabled = True
        self.max_zoom_out = 0.5
        self.max_zoom_in = 10
        #self.zoom_factor = None
        self.zoom_factor = 1.0

        # needs to be overridden in the child class
        self.measure = None

    def mousePressEvent(self, event: QMouseEvent):
        if self.zooming_enabled and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.mouse_pressed = True
                self.panning_mouse_pressed = True
                self.last_mouse_pos = event.pos()
        elif self.measuring_enabled and not self.leveling_key_pressed:
            self.measure.start_measurement(self.mapToScene(event.pos()))
        elif self.leveling_key_pressed and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.last_mouse_pos = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.zooming_enabled and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.mouse_pressed = False
                self.last_mouse_pos = None
            elif event.button() == Qt.MouseButton.RightButton:
                self.panning_mouse_pressed = False
                self.last_mouse_pos = None
        elif self.measure.is_measuring and not self.leveling_key_pressed:
            self.measure.end_measurement()
        elif self.leveling_key_pressed and not self.measure.is_measuring:
            if event.button() == Qt.MouseButton.LeftButton:
                self.last_mouse_pos = None
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Z:
            self.zoom_key_pressed = True
        elif event.key() == Qt.Key.Key_P:
            self.panning_key_pressed = True
        elif event.key() == Qt.Key.Key_M and self.measure.is_measuring:
            log.warn(f"{self.__class__.__name__} - Measuring tool disabled")
            self.measure.end_measurement()
        elif event.key() == Qt.Key.Key_M and not self.measure.is_measuring:
            log.warn(f"{self.__class__.__name__} - Measuring tool enabled")
            cursor_pos = QCursor.pos()
            scene_pos = self.mapToScene(self.mapFromGlobal(cursor_pos))
            self.measure.start_measurement(scene_pos)
        elif event.key() == Qt.Key.Key_L:  # "L" key starts window leveling
            print("Starting window leveling")
            self.leveling_key_pressed = True
            if self.window_center is None or self.window_width is None:
                self.window_center = 128
                self.window_width = 256
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Z:
            self.zoom_key_pressed = False
        elif event.key() == Qt.Key.Key_P:
            self.panning_key_pressed = False
        elif event.key() == Qt.Key.Key_L:  # "L" key stops window leveling
            print("Stopping window leveling")
            self.leveling_key_pressed = False
        else:
            super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if not self.measure.is_measuring and not self.leveling_key_pressed:
            # handle zoom
            if (
                self.zoom_key_pressed
                and self.mouse_pressed
                and self.last_mouse_pos is not None
            ):
                current_pos = event.pos()
                delta_y = current_pos.y() - self.last_mouse_pos.y()
                self.zoom_factor = 1 + (delta_y * self.zoom_sensitivity)
                current_zoom = self.transform().m11()
                new_zoom = current_zoom * self.zoom_factor

                if self.max_zoom_out <= new_zoom <= self.max_zoom_in:
                    self.scale(self.zoom_factor, self.zoom_factor)
                    self.zoomChanged.emit(new_zoom)  # emit signal for the new zoom level

                self.last_mouse_pos = current_pos

            # handle pan
            if (
                self.panning_key_pressed
                and self.panning_mouse_pressed
                and self.last_mouse_pos is not None
            ):
                delta = event.pos() - self.last_mouse_pos
                h_pan = self.horizontalScrollBar().value() - delta.x()
                v_pan = self.verticalScrollBar().value() - delta.y()

                self.horizontalScrollBar().setValue(h_pan)
                self.verticalScrollBar().setValue(v_pan)

                self.panChanged.emit(h_pan, v_pan)
                self.last_mouse_pos = event.pos()

        # handle measuring tool
        elif self.measure.is_measuring and not self.leveling_key_pressed:
            log.warn(f"{self.__class__.__name__} - Measuring tool updating")
            self.measure.update_measurement(self.mapToScene(event.pos()))

        # handle window / level adjustments while "L" is being held
        elif self.leveling_key_pressed and not self.measure.is_measuring:
            if self.window_center is None or self.window_width is None:
                print("Window center or width not set")
                return

            if self.last_mouse_pos is not None:
                delta = event.pos() - self.last_mouse_pos
                self.last_mouse_pos = event.pos()

                self.window_center += delta.y()  # Adjust level (vertical movement)
                self.window_width += delta.x()  # Adjust window (horizontal movement)

                # Ensure window center and width do not go below minimum values
                self.window_center = max(0, self.window_center)  # Min window center is 0
                self.window_width = max(1, self.window_width)  # Min window width is 1

                self._displayArray(self.window_center, self.window_width)
                self.updateColorScale(self.window_center, self.window_width)
        else:
            super().mouseMoveEvent(event)
