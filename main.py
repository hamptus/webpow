import sys

from PIL import Image

from PySide2 import QtCore, QtWidgets, QtGui


class Converter(QtCore.QRunnable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        parent = self.parent
        parent.quality_slider.setEnabled(False)
        parent.button.setEnabled(False)
        quality = parent.quality_slider.value()

        try:
            max_width = int(parent.max_width or parent.max_height)
            max_height = int(parent.max_height or parent.max_width)
        except (ValueError, TypeError):
            max_width = max_height = None

        filenames = parent.filename_list

        try:

            while filenames.count() > 0:
                item = filenames.takeItem(0)

                filename = item.text()
                outfile = filename + '.webp'

                with Image.open(filename) as img:
                    if max_width and max_height:
                        img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                    img.save(outfile, quality=quality, method=6)
        except Exception as e:
            print(e)
        finally:
            parent.filenames = []
            parent.quality_slider.setEnabled(True)
            parent.button.setEnabled(True)


class SizeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.container = QtWidgets.QHBoxLayout()

        self.width_layout = QtWidgets.QVBoxLayout()
        self.height_layout = QtWidgets.QVBoxLayout()

        self.width_layout.addWidget(QtWidgets.QLabel('Width'))
        self.height_layout.addWidget(QtWidgets.QLabel('Height'))

        self.max_width = QtWidgets.QLineEdit()
        self.max_width.setValidator(QtGui.QIntValidator())
        self.max_width.setToolTip(
            'The maximum width of the image. Aspect ratio will be maintained.')

        self.width_layout.addWidget(self.max_width)

        self.max_height = QtWidgets.QLineEdit()
        self.max_height.setValidator(QtGui.QIntValidator())
        self.max_height.setToolTip(
            'The maximum height of the image. Aspect ratio will be maintained.')

        self.height_layout.addWidget(self.max_height)

        self.container.addLayout(self.width_layout)
        self.container.addLayout(self.height_layout)
        self.layout.addLayout(self.container)
        self.layout.addWidget(QtWidgets.QLabel(
            '<em><strong>Note</strong>: Aspect ratio is maintained when resizing output</em>')  # noqa: e501
        )
        self.layout.addSpacing(20)

        self.layout.setMargin(0)

        self.setLayout(self.layout)

        # NOTE: Uncomment the following lines to preserve space when resize is
        # hidden

        # policy = self.sizePolicy()
        # policy.setRetainSizeWhenHidden(True)
        # self.setSizePolicy(policy)


class QualityLabelLayout(QtWidgets.QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addWidget(QtWidgets.QLabel('Quality:'))

        self.quality = QtWidgets.QLabel('80')
        self.addWidget(self.quality)

        self.setStretch(1, 1)


class QualitySlider(QtWidgets.QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setValue(80)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setTickInterval(10)
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)


class QualitySliderWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setMargin(0)
        self.setLayout(self.layout)

        self.label_layout = QualityLabelLayout()
        self.layout.addLayout(self.label_layout)

        self.quality = self.label_layout.quality

        self.slider = QualitySlider()
        self.slider.valueChanged.connect(
            lambda e: self.quality.setText(str(e))
        )

        self.layout.addWidget(self.slider)

    def value(self):
        return self.slider.value()


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()

        self.filenames = []

        self._add_menu()

        self.button = QtWidgets.QPushButton("Convert to Webp")

        self.quality_slider = QualitySliderWidget()

        self.setWindowTitle('WebPow - The easiest way to convert your images to WebP')

        self.filename_list = QtWidgets.QListWidget()
        self.layout.addWidget(QtWidgets.QLabel('Drop Images in the Box Below'))
        self.layout.addWidget(self.filename_list)

        self.resize_image = QtWidgets.QCheckBox()
        self.resize_image.stateChanged.connect(self.toggle_resize)

        self.resize_layout = QtWidgets.QHBoxLayout()
        self.resize_layout.addWidget(QtWidgets.QLabel('Resize Output'))
        self.resize_layout.addWidget(self.resize_image)
        self.resize_layout.addStretch()

        self.layout.addLayout(self.resize_layout)

        self.size_widget = SizeWidget()
        self.size_widget.setVisible(False)

        self.layout.addWidget(self.size_widget)

        self.layout.addWidget(self.quality_slider)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.button)

        self.layout.addLayout(self.button_layout)
        self.layout.setStretch(1, 1)

        self.setLayout(self.layout)

        self.button.clicked.connect(self.convert_images)
        self.setAcceptDrops(True)

        self.threadpool = QtCore.QThreadPool()

    def _add_menu(self):
        self.menubar = QtWidgets.QMenuBar()
        self.filemenu = QtWidgets.QMenu('&File')
        self.menubar.addMenu(self.filemenu)

        self.filemenu.addAction('&Add File', self._add_file)

    def _add_file(self):
        self._add_filename(
            QtWidgets.QFileDialog.getOpenFileName(self, "Open Image")[0]
        )

    @property
    def max_width(self):
        if self.resize_image.isChecked():
            return self.size_widget.max_width.text()

    @property
    def max_height(self):
        if self.resize_image.isChecked():
            return self.size_widget.max_height.text()

    def toggle_resize(self):
        self.size_widget.setVisible(self.resize_image.isChecked())

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                self._add_filename(url.toLocalFile())
        else:
            event.ignore()

    def convert_images(self):
        converter = Converter(self)
        self.threadpool.start(converter)

    def _add_filename(self, filename):
        if filename and filename not in self.filenames:
            QtWidgets.QListWidgetItem(filename, self.filename_list)
            self.filenames.append(filename)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 600)
    widget.show()

    sys.exit(app.exec_())
