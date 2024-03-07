import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QListWidget,  QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QSizePolicy
from PyQt5.QtGui import QPainter, QPixmap, QImage, QResizeEvent, QColor
from PyQt5.QtCore import Qt, pyqtSignal,  QByteArray, QMimeData, QDataStream
import numpy as np



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.centralWidget = QWidget(self)

        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.setCentralWidget(self.centralWidget)

        self._scanlistListWidget = QListWidget()
        self.layout.addWidget(self._scanlistListWidget, stretch=1)

        self._imageLabel = ImageLabel()
        self.layout.addWidget(self._imageLabel, stretch=2)
        

#QGraphicsView is a Qt class designed to display the contents of a QGraphicsScene. It provides a 2D view of the scene and allows users to interact with the items within the scene. 
class ImageLabel(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.model_data = None

        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually. 
        self.scene = QGraphicsScene(self)

        # Creates a pixmap graphics item that will be added to the scene
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # Sets the created scene as the scene for the graphics view
        self.setScene(self.scene)

        # Sets the render hint to enable antialiasing, which makes the image look smoother. Aliasings occur when a high-resolution image is displayed or rendered at a lower resolution, leading to the loss of information and the appearance of stair-stepped edges. Antialiasing techniques smooth out these jagged edges by introducing intermediate colors or shades along the edges of objects.
        self.setRenderHint(QPainter.Antialiasing, True)

        # Set the background color to black
        self.setBackgroundBrush(QColor(0, 0, 0))  # RGB values for black

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Initialize array attribute to None
        self.array = None
        self.current_slice = None

                # Enable drop events
        self.setAcceptDrops(True)

    # Override drag enter event to accept drops only if they're coming from QListWidget
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    # Override drop event to handle dropping items from QListWidget
    def dropEvent(self, event):
        # Retrieve the dropped data
        mimeData = event.mimeData()
        itemData = mimeData.data('application/x-qabstractitemmodeldatalist')
        dataStream = QDataStream(itemData)

        # Iterate over dropped items
        while not dataStream.atEnd():
            row = dataStream.readInt32()
            column = dataStream.readInt32()
            item = self._scanlistListWidget.item(row)

            # Display corresponding array if dropped onto ImageLabel
            if self.rect().contains(event.pos()) and item is not None:
                array_name = item.text()
                if array_name in self.model_data:
                    array = self.model_data[array_name]
                    self.setArray(array)
                    self.displayArray()

            event.accept()

        super().dropEvent(event)

    # This method is called whenever the graphics view is resized. It ensures that the image is always scaled to fit the view.
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    # overriden method from QGraphicsView. QGraphicsView has inherited QWidget's wheelEvent method. QGraphicsView is a child of QWidget. 
    def wheelEvent(self, event):
        # Check if the event occurred over the image
        if self.pixmap_item.isUnderMouse():
            # angleDelta().y() provides the angle through which the vertical mouse wheel was rotated since the last event in eigths of a degree. The value is positive when the wheel is rotated away from the user and negative when the wheel is rotated towards the user. 120 units * 1/8 = 15 degrees for most mouses. 
            delta = event.angleDelta().y() / 120
            current_slice = getattr(self, 'current_slice', 0)
            new_slice = max(0, min(current_slice + delta, self.array.shape[2] - 1))
            self.current_slice = int(new_slice)
            self.displayArray()
        else:
            # Allow the base class to handle the event in other cases
            super().wheelEvent(event)

    #ImageLabel holds a copy of the array of MRI data to be displayed. 
    def setArray(self, array):
        # Set the array and make current_slice the middle slice by default
        self.array = array
        if array is not None:
            self.current_slice = array.shape[2] // 2    
        else:
            self.current_slice = 0
            
    def displayArray(self):
        width, height = 0, 0
        if self.array is not None:
            displayed_slice = getattr(self, 'current_slice', 0)

            # Normalize the slice values for display
            array_norm = (self.array[:,:,displayed_slice] - np.min(self.array)) / (np.max(self.array) - np.min(self.array))
            array_8bit = (array_norm * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

        else:
            # Set a black image when self.array is None
            black_image = QImage(1, 1, QImage.Format_Grayscale8)
            black_image.fill(Qt.black)
            pixmap = QPixmap.fromImage(black_image)
            self.pixmap_item.setPixmap(pixmap)           

        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

        # Adjust the scene rectangle and center the image.  The arguments (0, 0, width, height) specify the left, top, width, and height of the scene rectangle.
        self.scene.setSceneRect(0, 0, width, height)
        # The centerOn method is used to center the view on a particular point within the scene.
        self.centerOn(width / 2, height / 2)
        

class App(QApplication):
    '''Main application class.'''
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.main_view = MainWindow()
        self.main_view.show()

        jsonFilePath = 'repository/models/models.json'
        self.model_data = Loader.load(jsonFilePath)
        model_names = list(self.model_data.keys())
        model = self.model_data[model_names[0]]

        t1map_file_path = model["T1mapFilePath"]
        t2map_file_path = model["T2mapFilePath"]
        pdmap_file_path = model["PDmapFilePath"]
        t1map = np.load(t1map_file_path)
        t2map = np.load(t2map_file_path)
        pdmap = np.load(pdmap_file_path)
        print(model)

        dict = {"T1map": t1map, "T2map": t2map, "PDmap": pdmap}

        for key, value in dict.items():
            self.main_view._scanlistListWidget.addItem(key)

        self.main_view._imageLabel.model_data = dict 

import json

class Loader:
    @staticmethod
    def load(jsonFilePath):
        with open(jsonFilePath, 'r') as json_file:
            data = json.load(json_file)
        return data

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())