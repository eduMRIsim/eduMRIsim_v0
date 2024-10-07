import numpy as np
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QGraphicsPolygonItem, QGraphicsPixmapItem


class StacksItem(QGraphicsPolygonItem):
    """Represents the intersection of the yellow middle stack of the volume with the image in the viewer as a polygon."""

    def __init__(self, parent: QGraphicsPixmapItem):
        super().__init__(parent)
        self.setPen(Qt.GlobalColor.yellow)

    def setPolygon(self, polygon_in_polygon_coords: QPolygonF):
        super().setPolygon(polygon_in_polygon_coords)
        self.previous_position_in_pixmap_coords = self.pos()

    def setPolygonFromPixmapCoords(self, polygon_in_pixmap_coords: list[np.array]):
        polygon_in_polygon_coords = QPolygonF()
        for pt in polygon_in_pixmap_coords:
            pt_in_polygon_coords = self.mapFromParent(QPointF(pt[0], pt[1]))
            polygon_in_polygon_coords.append(pt_in_polygon_coords)
        self.setPolygon(polygon_in_polygon_coords)
