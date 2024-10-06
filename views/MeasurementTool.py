import math

class MeasurementTool:
    def __init__(self, line_item, text_item):
        self.start_point = None
        self.end_point = None
        self.line_item = line_item
        self.text_item = text_item
        self.hide_items()
        self.is_measuring = False

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
            self.text_item.setPlainText(f"{distance:.2f} px")
            self.text_item.setPos((self.start_point + self.end_point) / 2)

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)