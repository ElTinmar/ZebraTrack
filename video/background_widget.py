# widget to specify a background subtraction method

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QLineEdit, QComboBox, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from video.background import BackgroundSubtractor, StaticBackground, DynamicBackground, DynamicBackgroundMP
from video.video_reader import OpenCV_VideoReader
from gui.custom_widgets.labeled_spinbox import LabeledSpinBox
from gui.custom_widgets.labeled_editline_openfile import FileOpenLabeledEditButton


class BackgroundSubtractorWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = None
        self.declare_components()
        self.layout_components()

    def declare_components(self):
        self.static_filename = FileOpenLabeledEditButton()
        self.static_numsamples = LabeledSpinBox()
        self.static_numsamples.setText('Number images')

        self.parameters_static = QWidget()
        self.parameters_dynamic = QWidget()
        self.parameters_dynamic_mp = QWidget()
        
        # drop-down list to choose the background subtraction method
        self.bckgsub_method_combobox = QComboBox(self)
        self.bckgsub_method_combobox.addItem('static')
        self.bckgsub_method_combobox.addItem('dynamic')
        self.bckgsub_method_combobox.addItem('dynamic mp')
        self.bckgsub_method_combobox.currentIndexChanged.connect(self.on_method_change)

        self.bckgsub_parameter_stack = QStackedWidget(self)
        self.bckgsub_parameter_stack.addWidget(self.parameters_static)
        self.bckgsub_parameter_stack.addWidget(self.parameters_dynamic)
        self.bckgsub_parameter_stack.addWidget(self.parameters_dynamic_mp)

    def layout_components(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.bckgsub_method_combobox)
        main_layout.addWidget(self.bckgsub_parameter_stack)

        static_layout = QVBoxLayout(self.parameters_static)
        static_layout.addWidget(self.static_filename)
        static_layout.addWidget(self.static_numsamples)


    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Select video file')
        self.static_filename.setText(file_name)

    def on_method_change(self, index):
        self.bckgsub_parameter_stack.setCurrentIndex(index)

    def update_background_subtractor(self):
        pass

    def get_background_subtractor(self):
        pass
