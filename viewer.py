import sys

from PIL import Image

from PySide2 import QtCore, QtWidgets, QtGui


class WebPViewer(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.container = QtWidgets.QLabel('Test')
        self.container.setAlignment(QtCore.Qt.AlignCenter)
        # self.pixmap = QtGui.QPixmap('images.jpeg.webp')
        #
        # self.container.setPixmap(self.pixmap)
        self.layout.addWidget(self.container)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = WebPViewer()
    widget.show()

    sys.exit(app.exec_())
