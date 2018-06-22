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

class WebPViewer(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        logger.debug('Starting WebPViewer')

        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.container = QtWidgets.QLabel()
        self.container.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.container)
        SIGNALS.file_open_signal.connect(self._open_pixmap)

    def _open_pixmap(self, filename):
        logger.debug('Opening Pixmap')
        logger.debug(filename)
        self.pixmap = QtGui.QPixmap(filename)
        self.container.setPixmap(self.pixmap)


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

    widget = WebPViewer()
    widget.show()

    sys.exit(app.exec_())
