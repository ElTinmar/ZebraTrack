from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from ..trackers.eyes import EyesTracker, EyesTrackerParamOverlay, EyesTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from .helper.ndarray_to_qpixmap import NDarray_to_QPixmap
from .custom_widgets.labeled_doublespinbox import LabeledDoubleSpinBox

class EyesTrackerWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = None
        self.declare_components()
        self.layout_components()

    def declare_components(self):
        self.image = QLabel(self)
        self.mask = QLabel(self)
        self.image_overlay = QLabel(self)
    
        # eye gamma
        self.eye_gamma = LabeledDoubleSpinBox(self)
        self.eye_gamma.setText('eye gamma')
        self.eye_gamma.setRange(0,100)
        self.eye_gamma.setValue(3.0)
        self.eye_gamma.valueChanged.connect(self.update_tracker) 

        # eye constrast
        self.eye_contrast = LabeledDoubleSpinBox(self)
        self.eye_contrast.setText('eye contrast')
        self.eye_contrast.setRange(0,100)
        self.eye_contrast.setValue(1.5)
        self.eye_contrast.valueChanged.connect(self.update_tracker) 

        # eye norm
        self.eye_norm = LabeledDoubleSpinBox(self)
        self.eye_norm.setText('eye norm')
        self.eye_norm.setRange(0,1)
        self.eye_norm.setValue(0.2)
        self.eye_norm.valueChanged.connect(self.update_tracker) 

        # eye size
        self.eye_size_lo_mm = LabeledDoubleSpinBox(self)
        self.eye_size_lo_mm.setText('min. eye size')
        self.eye_size_lo_mm.setRange(0,100)
        self.eye_size_lo_mm.setValue(0.8)
        self.eye_size_lo_mm.valueChanged.connect(self.update_tracker) 

        self.eye_size_hi_mm = LabeledDoubleSpinBox(self)
        self.eye_size_hi_mm.setText('max. eye size')
        self.eye_size_hi_mm.setRange(0,100)
        self.eye_size_hi_mm.setValue(10)
        self.eye_size_hi_mm.valueChanged.connect(self.update_tracker) 

        # crop_dimension_mm 
        self.crop_dimension_x_mm = LabeledDoubleSpinBox(self)
        self.crop_dimension_x_mm.setText('crop X (mm)')
        self.crop_dimension_x_mm.setRange(0,3)
        self.crop_dimension_x_mm.setValue(1)
        self.crop_dimension_x_mm.valueChanged.connect(self.update_tracker)

        self.crop_dimension_y_mm = LabeledDoubleSpinBox(self)
        self.crop_dimension_y_mm.setText('crop Y (mm)')
        self.crop_dimension_y_mm.setRange(0,3)
        self.crop_dimension_y_mm.setValue(1.5)
        self.crop_dimension_y_mm.valueChanged.connect(self.update_tracker)

        # crop offset 
        self.crop_offset_mm = LabeledDoubleSpinBox(self)
        self.crop_offset_mm.setText('Y offset eyes')
        self.crop_offset_mm.setRange(-5,5)
        self.crop_offset_mm.setValue(-0.5)
        self.crop_offset_mm.valueChanged.connect(self.update_tracker) 

        # ditance eye - midline
        self.dist_eye_midline_mm = LabeledDoubleSpinBox(self)
        self.dist_eye_midline_mm.setText('eye - midline (mm)')
        self.dist_eye_midline_mm.setRange(0,3)
        self.dist_eye_midline_mm.setValue(0.1)
        self.dist_eye_midline_mm.valueChanged.connect(self.update_tracker)

    def layout_components(self):
        parameters = QVBoxLayout()
        parameters.addWidget(self.eye_gamma)
        parameters.addWidget(self.eye_contrast)
        parameters.addWidget(self.eye_norm)
        parameters.addWidget(self.eye_size_lo_mm)
        parameters.addWidget(self.eye_size_hi_mm)
        parameters.addWidget(self.crop_dimension_x_mm)
        parameters.addWidget(self.crop_dimension_y_mm)
        parameters.addWidget(self.crop_offset_mm)
        parameters.addWidget(self.dist_eye_midline_mm)    

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.mask)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = EyesTrackerParamOverlay(
            pix_per_mm = self.pix_per_mm.value(),
            eye_len_mm = 0.2,
            color_eye_left = (255,255,0),
            color_eye_right = (0,255,0),
            thickness = 2
        )
        tracker_param = EyesTrackerParamTracking(
            eye_gamma = self.eye_gamma.value(),
            eye_contrast = self.eye_contrast.value(),
            eye_norm = self.eye_norm.value(),
            eye_size_lo_mm = self.eye_size_lo_mm.value(),
            eye_size_hi_mm = self.eye_size_hi_mm.value(),
            crop_offset_mm = self.crop_offset_mm.value(),
            dist_eye_midline_mm = self.dist_eye_midline_mm.value(), 
            crop_dimension_mm = (self.crop_dimension_x_mm.value(), self.crop_dimension_y_mm.value()),
        )
        self.tracker = EyesTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, heading: NDArray, centroid: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, heading, centroid)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()
