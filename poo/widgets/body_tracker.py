from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from body import BodyTracker, BodyTrackerParamOverlay, BodyTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from ndarray_to_qpixmap import NDarray_to_QPixmap
from labeled_doublespinbox import LabeledDoubleSpinBox
from labeled_spinbox import LabeledSpinBox


class BodyTrackerWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = None
        self.declare_components()
        self.layout_components()

    def declare_components(self):
        self.image = QLabel(self)
        self.mask = QLabel(self)
        self.image_overlay = QLabel(self)
        
        # pix per mm
        self.pix_per_mm_label = QLabel(self)
        self.pix_per_mm_label.setText('pixels / mm')

        self.pix_per_mm_spinbox = QDoubleSpinBox(self)
        self.pix_per_mm_spinbox.setRange(0,1000)
        self.pix_per_mm_spinbox.setValue(40)
        self.pix_per_mm_spinbox.valueChanged.connect(self.update_tracker)

        # body intensity
        self.body_intensity_label = QLabel(self)
        self.body_intensity_label.setText('body intensity')

        self.body_intensity_spinbox = QDoubleSpinBox(self)
        self.body_intensity_spinbox.setRange(0,1)
        self.body_intensity_spinbox.setValue(0.08)
        self.body_intensity_spinbox.valueChanged.connect(self.update_tracker)

        # body size
        self.min_body_size_label = QLabel(self)
        self.min_body_size_label.setText('min body size (mm)')

        self.min_body_size_mm_spinbox = QDoubleSpinBox(self)
        self.min_body_size_mm_spinbox.setRange(0,10000)
        self.min_body_size_mm_spinbox.setValue(8)
        self.min_body_size_mm_spinbox.valueChanged.connect(self.update_tracker)

        #
        self.max_body_size_label = QLabel(self)
        self.max_body_size_label.setText('max body size (mm)')

        self.max_body_size_mm_spinbox = QDoubleSpinBox(self)
        self.max_body_size_mm_spinbox.setRange(0,10000)
        self.max_body_size_mm_spinbox.setValue(30)
        self.max_body_size_mm_spinbox.valueChanged.connect(self.update_tracker)

        # body length
        self.min_body_length_label = QLabel(self)
        self.min_body_length_label.setText('min body length (mm)')

        self.min_body_length_mm_spinbox = QDoubleSpinBox(self)
        self.min_body_length_mm_spinbox.setRange(0,100)
        self.min_body_length_mm_spinbox.setValue(2)
        self.min_body_length_mm_spinbox.valueChanged.connect(self.update_tracker)

        #
        self.max_body_length_label = QLabel(self)
        self.max_body_length_label.setText('max body length (mm)')

        self.max_body_length_mm_spinbox = QDoubleSpinBox(self)
        self.max_body_length_mm_spinbox.setRange(0,100)
        self.max_body_length_mm_spinbox.setValue(6)
        self.max_body_length_mm_spinbox.valueChanged.connect(self.update_tracker)

        # body width
        self.min_body_width_label = QLabel(self)
        self.min_body_width_label.setText('min body width (mm)')

        self.min_body_width_mm_spinbox = QDoubleSpinBox(self)
        self.min_body_width_mm_spinbox.setRange(0,100)
        self.min_body_width_mm_spinbox.setValue(0.4)
        self.min_body_width_mm_spinbox.valueChanged.connect(self.update_tracker)

        #
        self.max_body_width_label = QLabel(self)
        self.max_body_width_label.setText('max body width (mm)')

        self.max_body_width_mm_spinbox = QDoubleSpinBox(self)
        self.max_body_width_mm_spinbox.setRange(0,100)
        self.max_body_width_mm_spinbox.setValue(1.2)
        self.max_body_width_mm_spinbox.valueChanged.connect(self.update_tracker)

    def layout_components(self):

        row00 = QHBoxLayout()
        row00.addWidget(self.pix_per_mm_label)
        row00.addWidget(self.pix_per_mm_spinbox)
        
        row01 = QHBoxLayout()
        row01.addWidget(self.body_intensity_label)
        row01.addWidget(self.body_intensity_spinbox)

        row02 = QHBoxLayout()
        row02.addWidget(self.min_body_size_label)
        row02.addWidget(self.min_body_size_mm_spinbox)

        row03 = QHBoxLayout()
        row03.addWidget(self.max_body_size_label)
        row03.addWidget(self.max_body_size_mm_spinbox)

        row04 = QHBoxLayout()
        row04.addWidget(self.min_body_length_label)
        row04.addWidget(self.min_body_length_mm_spinbox)

        row05 = QHBoxLayout()
        row05.addWidget(self.max_body_length_label)
        row05.addWidget(self.max_body_length_mm_spinbox)

        row06 = QHBoxLayout()
        row06.addWidget(self.min_body_width_label)
        row06.addWidget(self.min_body_width_mm_spinbox)

        row07 = QHBoxLayout()
        row07.addWidget(self.max_body_width_label)
        row07.addWidget(self.max_body_width_mm_spinbox)

        parameters = QVBoxLayout()
        parameters.addLayout(row00)
        parameters.addLayout(row01)
        parameters.addLayout(row02)
        parameters.addLayout(row03)
        parameters.addLayout(row04)
        parameters.addLayout(row05)
        parameters.addLayout(row06)
        parameters.addLayout(row07)

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.mask)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = BodyTrackerParamOverlay(
            pix_per_mm = self.pix_per_mm_spinbox.value(),
            heading_len_mm = 1,
            heading_color = (255,0,255),
            thickness = 2
        )
        tracker_param = BodyTrackerParamTracking(
            pix_per_mm = self.pix_per_mm_spinbox.value(),
            body_intensity = self.body_intensity_spinbox.value(),
            min_body_size_mm = self.min_body_size_mm_spinbox.value(),
            max_body_size_mm = self.max_body_size_mm_spinbox.value(),
            min_body_length_mm = self.min_body_length_mm_spinbox.value(),
            max_body_length_mm = self.max_body_length_mm_spinbox.value(),
            min_body_width_mm = self.min_body_width_mm_spinbox.value(),
            max_body_width_mm = self.max_body_width_mm_spinbox.value()
        )
        self.tracker = BodyTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, offset)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()