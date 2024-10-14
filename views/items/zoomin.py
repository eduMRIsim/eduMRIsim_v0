from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QCursor
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene

from utils.logger import log


class ZoomableView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually.
        self.scene = QGraphicsScene(self)

        self.mouse_pressed = False
        self.panning_mouse_pressed = False
        self.zoom_key_pressed = False
        self.panning_key_pressed = False
        self.measuring_key_pressed = False
        self.last_mouse_pos = None
        self.zoom_sensitivity = 0.005
        self.measuring_enabled = False
        self.zooming_enabled = True
        self.max_zoom_out = 0.5
        self.max_zoom_in = 10
        self.zoom_factor = None

        # needs to be overriden in the child class
        self.measure = None

    def mousePressEvent(self, event: QMouseEvent):
        if self.zooming_enabled and not self.measuring_enabled:
            if event.button() == Qt.MouseButton.LeftButton:
                self.mouse_pressed = True
                self.panning_mouse_pressed = True
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
            elif event.button() == Qt.MouseButton.RightButton:
                self.panning_mouse_pressed = False
                self.last_mouse_pos = None
        elif self.measure.is_measuring:
            self.measure.end_measurement()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if (
            self.zooming_enabled
            and not self.measuring_enabled
        ):
            if event.key() == Qt.Key.Key_Z:
                self.zoom_key_pressed = True
            elif event.key() == Qt.Key.Key_P:
                self.panning_key_pressed = True
        elif event.key() == Qt.Key.Key_M and self.measure.is_measuring:
            log.debug(f"{self.__class__.__name__} - Measuring tool disabled")
            self.measure.end_measurement()
        elif event.key() == Qt.Key.Key_M and not self.measure.is_measuring:
            log.debug(f"{self.__class__.__name__} - Measuring tool enabled")
            # The keypress event is registered but move the measuring tool is not started
            cursor_pos = QCursor.pos()
            scene_pos = self.mapToScene(self.mapFromGlobal(cursor_pos))

            self.measure.start_measurement(scene_pos)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if (
            self.zooming_enabled
            and self.measuring_enabled == False
        ):
            if event.key() == Qt.Key.Key_Z:
                self.zoom_key_pressed = False
            elif event.key() == Qt.Key.Key_P:
                self.panning_key_pressed = False
        if event.key() == Qt.Key.Key_M:
            self.measuring_key_pressed = False
        else:
            super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.zooming_enabled
            and not self.measuring_enabled
        ):
            # handle zoom
            if self.zoom_key_pressed and self.mouse_pressed and self.last_mouse_pos is not None:
                current_pos = event.pos()

                delta_y = current_pos.y() - self.last_mouse_pos.y()
                self.zoom_factor = 1 + (delta_y * self.zoom_sensitivity)

                current_zoom = self.transform().m11()
                new_zoom = current_zoom * self.zoom_factor

                if self.max_zoom_out <= new_zoom <= self.max_zoom_in:
                    self.scale(self.zoom_factor, self.zoom_factor)

                self.last_mouse_pos = current_pos
            # handle pan
            if self.panning_key_pressed and self.panning_mouse_pressed and self.last_mouse_pos is not None:
                delta = event.pos() - self.last_mouse_pos

                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

                self.last_mouse_pos = event.pos()

        # handle measuring tool
        elif self.measure.is_measuring:
            self.measure.update_measurement(self.mapToScene(event.pos()))
        else:
            super().mouseMoveEvent(event)