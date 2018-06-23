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


class PhotoLabel(QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_pixmap = None

    def resizeEvent(self, event):
        try:
            self.setPixmap(self.source_pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            ))
        except AttributeError:
            pass


class PhotoViewer(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        logger.debug('Starting PhotoViewer')

        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()

        self.container = PhotoLabel()
        self.container.setAlignment(QtCore.Qt.AlignCenter)

        self.container.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.setAcceptDrops(True)

        self.resize(QtGui.QGuiApplication.primaryScreen().availableSize() * 3/5)

        SIGNALS.file_open_signal.connect(self._open_pixmap)

    def _open_pixmap(self, filename):
        logger.debug('Opening Pixmap')
        logger.debug(filename)

        self.container.source_pixmap = QtGui.QPixmap(filename)
        self.container.setPixmap(
            self.container.source_pixmap.scaled(
                self.container.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            self._open_pixmap(event.mimeData().urls()[0].toLocalFile())
        else:
            event.ignore()


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
