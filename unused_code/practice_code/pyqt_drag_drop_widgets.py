from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

'''
Q: In this example, what data is being transferred during the drag operation? 
A: The QMimeData object (mime) is associated with the QDrag object (drag) using the setMimeData method. However, in the provided code, no custom data is set within the QMimeData object. Instead, it's left empty, indicating that no additional data beyond the widget itself is being transferred.
'''

class DragButton(QPushButton):
    #Overrides the mouseMoveEvent method of the button widget. This method is called when the mouse moves over the button.
    def mouseMoveEvent(self, e):

        #Checks if the left mouse button is pressed (Qt.LeftButton). Dragging is only initiated if the left button is pressed.
        if e.buttons() == Qt.LeftButton:
            #Creates a QDrag object to handle the drag operation. The self argument specifies the parent widget of the drag object, which is the button itself.
            drag = QDrag(self)
            #Creates a QMimeData object to hold the data being dragged. This object can store arbitrary data associated with the drag operation.
            mime = QMimeData()
            #Associates the QMimeData object with the drag object. This sets the data that will be transferred during the drag operation.
            drag.setMimeData(mime)
            #Initiates the drag operation. Qt.MoveAction specifies that the drag operation will move the data rather than copy it.    
            drag.exec_(Qt.MoveAction)


class Window(QWidget):

    def __init__(self):
        super().__init__()
        #Enables this widget to accept drop events. This means that it can receive items dropped onto it from other widgets.
        self.setAcceptDrops(True)

        self.blayout = QHBoxLayout()
        for l in ['A', 'B', 'C', 'D']:
            btn = DragButton(l)
            self.blayout.addWidget(btn)

        self.setLayout(self.blayout)

    # Overrides the dragEnterEvent method of the widget. This method is called when a drag enters the widget. In this case, it simply accepts the drag event.
    def dragEnterEvent(self, e):
        e.accept()

    # Overrides the dropEvent method of the widget. This method is called when an item is dropped onto the widget.
    def dropEvent(self, e):
        # Retrieves the position (pos) where the item was dropped within the widget.
        pos = e.pos()
        # Retrieves the source widget (widget) of the drop event. This is the widget from which the item was dragged.
        widget = e.source()

        # Iterates over the buttons in the horizontal box layout blayout.
        for n in range(self.blayout.count()):
            # Retrieves the widget w at each index in the layout. In this case, it retrieves each button widget.
            w = self.blayout.itemAt(n).widget()

            # Checks if the x-coordinate of the drop position is less than the x-coordinate of the middle point of the current button widget w. This determines whether the item was dropped to the left or right of the button.
            if pos.x() < w.x() + w.size().width() // 2:
                # Inserts the dragged widget (widget) into the horizontal box layout blayout at the position determined by n-1. This effectively moves the dragged item to the left of the current button widget.
                self.blayout.insertWidget(n-1, widget)
                #Exits the loop once the item has been inserted into the layout.
                break

        # Accepts the drop event, indicating that the drop operation was successful.        
        e.accept()


app = QApplication([])
w = Window()
w.show()

app.exec_()