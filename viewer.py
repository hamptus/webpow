import sys
import logging
import pathlib
from functools import partial

from PIL import Image

from PySide2 import QtCore, QtWidgets, QtGui

HOME = pathlib.Path.home()
LOG_DIR = HOME.joinpath('Library/Logs')
LOG_FILE = LOG_DIR.joinpath('viewer.log')

logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Signals(QtCore.QObject):
    file_open_signal = QtCore.Signal(str)


SIGNALS = Signals()


class Container(QtWidgets.QScrollArea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PhotoLabel(QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def resizeEvent(self, event):
    #     try:
    #         self.setPixmap(self.source_pixmap.scaled(
    #             self.size(),
    #             QtCore.Qt.KeepAspectRatio,
    #             QtCore.Qt.SmoothTransformation,
    #         ))
    #     except AttributeError:
    #         pass


class PhotoViewer(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        logger.debug('Starting PhotoViewer')

        super().__init__(*args, **kwargs)

        self.container = Container()
        self.setCentralWidget(self.container)

        self.label = PhotoLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setScaledContents(True)

        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.container.setWidget(self.label)
        self.container.setAlignment(QtCore.Qt.AlignCenter)

        self.setAcceptDrops(True)

        self.resize(QtGui.QGuiApplication.primaryScreen().availableSize() * 3/5)

        SIGNALS.file_open_signal.connect(self._open_pixmap)


    def _open_pixmap(self, filename):
        logger.debug('Opening Pixmap')
        logger.debug(filename)

        image_reader = QtGui.QImageReader(filename)
        # image_reader.setAutoTransform(True)
        new_image = image_reader.read()

        self.label.setPixmap(QtGui.QPixmap.fromImage(new_image))
        # self.label.adjustSize()

        self._resize_pixmap()

    def _resize_pixmap(self):
        pixmap = self.label.pixmap()
        try:
            aspect = self.width() / self.height()
            pixmap_ratio = pixmap.width() / pixmap.height()

            if aspect > pixmap_ratio:
                new_width = pixmap_ratio * self.height()
                new_height = self.height()
            else:
                new_height = self.width() / pixmap_ratio
                new_width = self.width()

            self.label.resize(new_width, new_height)
        except AttributeError:
            pass

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            self._open_pixmap(event.mimeData().urls()[0].toLocalFile())
        else:
            event.ignore()

    def resizeEvent(self, event):
        self._resize_pixmap()


class App(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event(self, event):
        if isinstance(event, QtGui.QFileOpenEvent):
            logger.info('QFileOpenEvent Fired')
            SIGNALS.file_open_signal.emit(event.file())
        return super().event(event)


if __name__ == "__main__":
    app = App(sys.argv)

    widget = PhotoViewer()
    # widget.resize(350, 350)
    widget.show()

    sys.exit(app.exec_())
