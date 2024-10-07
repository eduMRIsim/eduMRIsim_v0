import math

class MeasurementTool:
    def __init__(self, line_item, text_item, ac_series):
        self.start_point = None
        self.end_point = None
        self.line_item = line_item
        self.text_item = text_item
        self.hide_items()
        self.is_measuring = False
        self.ac_series = ac_series

    def hide_items(self):
        self.line_item.setVisible(False)
        self.text_item.setVisible(False)

    def show_items(self):
        self.line_item.setVisible(True)
        self.text_item.setVisible(True)

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
            self.line_item.setLine(self.start_point.x(), self.start_point.y(), self.end_point.x(), self.end_point.y())
            distance = self.calculate_distance(self.start_point, self.end_point)
            self.text_item.setPlainText(f"{distance:.2f} mm")
            self.text_item.setPos((self.start_point + self.end_point) / 2)

    def calculate_distance(self, p1, p2):
        p1_mm_coords = self.ac_series.displayed_image.image_geometry.pixmap_coords_to_image_mm_coords((p1.x(), p1.y()))
        p2_mm_coords = self.ac_series.displayed_image.image_geometry.pixmap_coords_to_image_mm_coords((p2.x(), p2.y()))

        dist = math.sqrt((p2_mm_coords[0] - p1_mm_coords[0]) ** 2 + (p2_mm_coords[1] - p1_mm_coords[1]) ** 2)
        return dist