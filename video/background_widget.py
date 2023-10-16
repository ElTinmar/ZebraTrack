# widget to specify a background subtraction method

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QLineEdit, QComboBox, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from video.background import BackgroundSubtractor, NoBackgroundSub, BackroundImage, StaticBackground, DynamicBackground, DynamicBackgroundMP
from video.video_reader import OpenCV_VideoReader
from gui.custom_widgets.labeled_spinbox import LabeledSpinBox
from gui.custom_widgets.labeled_editline_openfile import FileOpenLabeledEditButton

# TODO define protocol or import ABC for BackgroundSubtractor

class BackgroundSubtractorWidget(QWidget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_subtractor = None
        self.declare_components()
        self.layout_components()
        self.update_background_subtractor()

    def declare_components(self):

        # none
        self.parameters_none = QWidget()

        # image background
        self.parameters_image = QWidget()
        self.image_filename = FileOpenLabeledEditButton()

        # static background
        self.parameters_static = QWidget()
        self.static_filename = FileOpenLabeledEditButton()
        self.static_filename.textChanged.connect(self.update_background_subtractor)
        self.static_numsamples = LabeledSpinBox()
        self.static_numsamples.setText('Number images')
        self.static_numsamples.setRange(1,10000)
        self.static_numsamples.setValue(10)
        self.static_numsamples.valueChanged.connect(self.update_background_subtractor)

        # dynamic background    
        self.parameters_dynamic = QWidget()
        self.dynamic_numsamples = LabeledSpinBox()
        self.dynamic_numsamples.setText('Number images')
        self.dynamic_numsamples.setRange(1,10000)
        self.dynamic_numsamples.setValue(10)
        self.dynamic_numsamples.valueChanged.connect(self.update_background_subtractor)
        self.dynamic_samplefreq = LabeledSpinBox()
        self.dynamic_samplefreq.setText('Frequency')
        self.dynamic_samplefreq.setRange(1,10000)
        self.dynamic_samplefreq.setValue(10)
        self.dynamic_samplefreq.valueChanged.connect(self.update_background_subtractor)
        
        # dynamic multiprocessing
        self.parameters_dynamic_mp = QWidget()
        self.dynamic_mp_numsamples = LabeledSpinBox()
        self.dynamic_mp_numsamples.setText('Number images')
        self.dynamic_mp_numsamples.setRange(1,10000)
        self.dynamic_mp_numsamples.setValue(10)
        self.dynamic_mp_numsamples.valueChanged.connect(self.update_background_subtractor)
        self.dynamic_mp_samplefreq = LabeledSpinBox()
        self.dynamic_mp_samplefreq.setText('Frequency')
        self.dynamic_mp_samplefreq.setRange(1,10000)
        self.dynamic_mp_samplefreq.setValue(10)
        self.dynamic_mp_samplefreq.valueChanged.connect(self.update_background_subtractor)
        self.dynamic_mp_width = LabeledSpinBox()
        self.dynamic_mp_width.setText('Width')
        self.dynamic_mp_width.setRange(1,10000)
        self.dynamic_mp_width.setValue(10)
        self.dynamic_mp_width.valueChanged.connect(self.update_background_subtractor)
        self.dynamic_mp_height = LabeledSpinBox()
        self.dynamic_mp_height.setText('Height')
        self.dynamic_mp_height.setRange(1,10000)
        self.dynamic_mp_height.setValue(10)
        self.dynamic_mp_height.valueChanged.connect(self.update_background_subtractor)
        
        # drop-down list to choose the background subtraction method
        self.bckgsub_method_combobox = QComboBox(self)
        self.bckgsub_method_combobox.addItem('none')
        self.bckgsub_method_combobox.addItem('image')
        self.bckgsub_method_combobox.addItem('static')
        self.bckgsub_method_combobox.addItem('dynamic')
        self.bckgsub_method_combobox.addItem('dynamic mp')
        self.bckgsub_method_combobox.currentIndexChanged.connect(self.on_method_change)

        self.init_button = QPushButton('initialize', self)
        self.init_button.clicked.connect(self.initialize_background_subtractor)

        self.bckgsub_parameter_stack = QStackedWidget(self)
        self.bckgsub_parameter_stack.addWidget(self.parameters_none)
        self.bckgsub_parameter_stack.addWidget(self.parameters_image)
        self.bckgsub_parameter_stack.addWidget(self.parameters_static)
        self.bckgsub_parameter_stack.addWidget(self.parameters_dynamic)
        self.bckgsub_parameter_stack.addWidget(self.parameters_dynamic_mp)

    def layout_components(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.bckgsub_method_combobox)
        main_layout.addWidget(self.bckgsub_parameter_stack)
        main_layout.addWidget(self.init_button)

        image_layout = QVBoxLayout(self.parameters_image)
        image_layout.addWidget(self.image_filename)
        image_layout.addStretch()

        static_layout = QVBoxLayout(self.parameters_static)
        static_layout.addWidget(self.static_filename)
        static_layout.addWidget(self.static_numsamples)
        static_layout.addStretch()

        dynamic_layout = QVBoxLayout(self.parameters_dynamic)
        dynamic_layout.addWidget(self.dynamic_numsamples)
        dynamic_layout.addWidget(self.dynamic_samplefreq)
        dynamic_layout.addStretch()

        dynamic_mp_layout = QVBoxLayout(self.parameters_dynamic_mp)
        dynamic_mp_layout.addWidget(self.dynamic_mp_numsamples)
        dynamic_mp_layout.addWidget(self.dynamic_mp_samplefreq)
        dynamic_mp_layout.addWidget(self.dynamic_mp_height)
        dynamic_mp_layout.addWidget(self.dynamic_mp_width)

    def on_method_change(self, index):
        self.bckgsub_parameter_stack.setCurrentIndex(index)
        self.update_background_subtractor()

    def update_background_subtractor(self):
        method = self.bckgsub_method_combobox.currentIndex()
        
        if method == 0:
            self.background_subtractor = NoBackgroundSub()

        if method == 1:
            self.background_subtractor = BackroundImage(
                image_file_name = self.image_filename.value()
            )
        
        if method == 2:
            video_reader = OpenCV_VideoReader()
            video_reader.open_file(self.static_filename.text())
            self.background_subtractor = StaticBackground(
                video_reader = video_reader,
                num_sample_frames = self.static_numsamples.value()
            )
        
        if method == 3:
            self.background_subtractor = DynamicBackground(
                num_sample_frames = self.dynamic_numsamples.value(),
                sample_every_n_frames = self.dynamic_samplefreq.value()
            )

        if method == 4:
            self.background_subtractor = DynamicBackgroundMP(
                num_images = self.dynamic_mp_numsamples.value(),
                every_n_image = self.dynamic_mp_samplefreq.value(),
                width = self.dynamic_mp_width.value(),
                height = self.dynamic_mp_height.value()
            )

    def initialize_background_subtractor(self):
        self.background_subtractor.initialize()

    def get_background_subtractor(self):
        return self.background_subtractor

