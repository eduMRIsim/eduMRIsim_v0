from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QImage, QResizeEvent, QColor
import numpy as np

class MyGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Create a scene and add a pixmap item
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setScene(self.scene)

    # overriden method from QGraphicsView. QGraphicsView has inherited QWidget's wheelEvent method. QGraphicsView is a child of QWidget. 
    def wheelEvent(self, event):
        # Check if the event occurred over the image
        if self.pixmap_item.isUnderMouse():
            delta = event.angleDelta().y() / 120
            current_slice = getattr(self, 'current_slice', 0)
            new_slice = max(0, min(current_slice + delta, self.array.shape[2] - 1))
            self.current_slice = int(new_slice)
            self.displayArray(self.array)
        else:
            # Allow the base class to handle the event in other cases
            super().wheelEvent(event)

    def displayArray(self, array):
        self.array = array
        middle_slice = array.shape[2] // 2
        displayed_slice = getattr(self, 'current_slice', middle_slice)
        
        print(array[:,:,displayed_slice].shape)

        array_norm = (array[:,:,displayed_slice] - np.min(array)) / (np.max(array) - np.min(array))
        array_8bit = (array_norm * 255).astype(np.uint8)

        image = np.ascontiguousarray(np.array(array_8bit))
        height, width = image.shape
        qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)

        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

        # Adjust the scene rectangle and center the image
        self.scene.setSceneRect(0, 0, width, height)
        self.centerOn(width / 2, height / 2)

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = MyGraphicsView()
    view.show()
    example_array = np.random.rand(100, 100, 10)
    print(example_array.shape[2] // 2)
    view.displayArray(example_array)
    sys.exit(app.exec_())