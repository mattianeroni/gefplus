from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtCore import Qt, QMimeData


class DragButton(QPushButton):

    """ An instance of this class represents a droppable button """

    def mouseMoveEvent(self, event):
        """ Implement the movement until the 
        left button is pressed """
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)