from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from ..tracker.body import BodyTracker, BodyTrackerParamOverlay, BodyTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from .helper.ndarray_to_qpixmap import NDarray_to_QPixmap
from .custom_widgets.labeled_doublespinbox import LabeledDoubleSpinBox

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
        self.pix_per_mm = LabeledDoubleSpinBox(self)
        self.pix_per_mm.setText('pixels / mm')
        self.pix_per_mm.setRange(0,1000)
        self.pix_per_mm.setValue(40)
        self.pix_per_mm.valueChanged.connect(self.update_tracker)

        # body intensity
        self.body_intensity = LabeledDoubleSpinBox(self)
        self.body_intensity.setText('body intensity')
        self.body_intensity.setRange(0,1)
        self.body_intensity.setValue(0.08)
        self.body_intensity.valueChanged.connect(self.update_tracker)

        # body size
        self.min_body_size_mm = LabeledDoubleSpinBox(self)
        self.min_body_size_mm.setText('min body size (mm)')
        self.min_body_size_mm.setRange(0,1000)
        self.min_body_size_mm.setValue(8)
        self.min_body_size_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_size_mm = LabeledDoubleSpinBox(self)
        self.max_body_size_mm.setText('max body size (mm)')
        self.max_body_size_mm.setRange(0,10000)
        self.max_body_size_mm.setValue(30)
        self.max_body_size_mm.valueChanged.connect(self.update_tracker)

        # body length
        self.min_body_length_mm = LabeledDoubleSpinBox(self)
        self.min_body_length_mm.setText('min body length (mm)')
        self.min_body_length_mm.setRange(0,100)
        self.min_body_length_mm.setValue(2)
        self.min_body_length_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_length_mm = LabeledDoubleSpinBox(self)
        self.max_body_length_mm.setText('max body length (mm)')
        self.max_body_length_mm.setRange(0,100)
        self.max_body_length_mm.setValue(6)
        self.max_body_length_mm.valueChanged.connect(self.update_tracker)

        # body width
        self.min_body_width_mm = LabeledDoubleSpinBox(self)
        self.min_body_width_mm.setText('min body width (mm)')
        self.min_body_width_mm.setRange(0,100)
        self.min_body_width_mm.setValue(0.4)
        self.min_body_width_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_width_mm = LabeledDoubleSpinBox(self)
        self.max_body_width_mm.setText('max body width (mm)')
        self.max_body_width_mm.setRange(0,100)
        self.max_body_width_mm.setValue(1.2)
        self.max_body_width_mm.valueChanged.connect(self.update_tracker)

    def layout_components(self):

        parameters = QVBoxLayout()
        parameters.addWidget(self.pix_per_mm)
        parameters.addWidget(self.body_intensity)
        parameters.addWidget(self.min_body_size_mm)
        parameters.addWidget(self.max_body_size_mm)
        parameters.addWidget(self.min_body_length_mm)
        parameters.addWidget(self.max_body_length_mm)
        parameters.addWidget(self.min_body_width_mm)
        parameters.addWidget(self.max_body_width_mm)

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.mask)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = BodyTrackerParamOverlay(
            pix_per_mm = self.pix_per_mm.value(),
            heading_len_mm = 1,
            heading_color = (255,0,255),
            thickness = 2
        )
        tracker_param = BodyTrackerParamTracking(
            pix_per_mm = self.pix_per_mm.value(),
            body_intensity = self.body_intensity.value(),
            min_body_size_mm = self.min_body_size_mm.value(),
            max_body_size_mm = self.max_body_size_mm.value(),
            min_body_length_mm = self.min_body_length_mm.value(),
            max_body_length_mm = self.max_body_length_mm.value(),
            min_body_width_mm = self.min_body_width_mm.value(),
            max_body_width_mm = self.max_body_width_mm.value()
        )
        self.tracker = BodyTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, offset)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()