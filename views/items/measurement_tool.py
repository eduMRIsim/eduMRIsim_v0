import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem


class MeasurementTool:
    def __init__(self, line_item, text_item, ac_series):
        self.start_point = None
        self.end_point = None
        self.line_item = line_item
        self.text_item = text_item
        self.is_measuring = False
        self.ac_series = ac_series

        self.start_dot = QGraphicsEllipseItem()
        self.end_dot = QGraphicsEllipseItem()
        self.scene = self.line_item.scene()
        self.scene.addItem(self.start_dot)
        self.scene.addItem(self.end_dot)
        self.start_dot.setBrush(QBrush(Qt.GlobalColor.red))
        self.end_dot.setBrush(QBrush(Qt.GlobalColor.red))

        self.hide_items()


    def hide_items(self):
        self.line_item.setVisible(False)
        self.text_item.setVisible(False)
        self.start_dot.setVisible(False)
        self.end_dot.setVisible(False)

    def show_items(self):
        self.line_item.setVisible(True)
        self.text_item.setVisible(True)
        self.start_dot.setVisible(True)
        self.end_dot.setVisible(True)

    def start_measurement(self, point):
        self.start_point = point
        self.end_point = point
        self.show_items()
        self.is_measuring = True
        self.update_measurement(point)

    def end_measurement(self):
        self.is_measuring = False

    def update_measurement(self, point):
        if self.start_point is not None:
            self.end_point = point
            self.line_item.setLine(
                self.start_point.x(),
                self.start_point.y(),
                self.end_point.x(),
                self.end_point.y(),
            )
            self.line_item.setPen(QPen(Qt.GlobalColor.red, 1))  # Make the line thinner

            distance = self.calculate_distance(self.start_point, self.end_point)
            self.text_item.setPlainText(f"{distance:.2f} mm")

            midpoint = (self.start_point + self.end_point) / 2

            self.text_item.setPos(midpoint.x(), midpoint.y() - 10)
            self.text_item.setZValue(1)

            self.start_dot.setRect(self.start_point.x() - 2, self.start_point.y() - 2, 4, 4)
            self.end_dot.setRect(self.end_point.x() - 2, self.end_point.y() - 2, 4, 4)

    def calculate_distance(self, p1, p2):
        p1_mm_coords = self.ac_series.displayed_image.image_geometry.pixmap_coords_to_image_mm_coords(
            (p1.x(), p1.y())
        )
        p2_mm_coords = self.ac_series.displayed_image.image_geometry.pixmap_coords_to_image_mm_coords(
            (p2.x(), p2.y())
        )

        dist = math.sqrt(
            (p2_mm_coords[0] - p1_mm_coords[0]) ** 2
            + (p2_mm_coords[1] - p1_mm_coords[1]) ** 2
        )
        return dist
