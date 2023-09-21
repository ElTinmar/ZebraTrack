from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from eyes import EyesTracker, EyesTrackerParamOverlay, EyesTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from ndarray_to_qpixmap import NDarray_to_QPixmap
from labeled_doublespinbox import LabeledDoubleSpinBox
from labeled_spinbox import LabeledSpinBox

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
        self.eye_gamma_label = QLabel(self)
        self.eye_gamma_label.setText('eye gamma')

        self.eye_gamma_spinbox = QDoubleSpinBox(self)
        self.eye_gamma_spinbox.setRange(0,100)
        self.eye_gamma_spinbox.setValue(3.0)
        self.eye_gamma_spinbox.valueChanged.connect(self.update_tracker) 

        # eye constrast
        self.eye_contrast_label = QLabel(self)
        self.eye_contrast_label.setText('eye contrast')

        self.eye_contrast_spinbox = QDoubleSpinBox(self)
        self.eye_contrast_spinbox.setRange(0,100)
        self.eye_contrast_spinbox.setValue(1.5)
        self.eye_contrast_spinbox.valueChanged.connect(self.update_tracker) 

        # eye norm
        self.eye_norm_label = QLabel(self)
        self.eye_norm_label.setText('eye norm')

        self.eye_norm_spinbox = QDoubleSpinBox(self)
        self.eye_norm_spinbox.setRange(0,1)
        self.eye_norm_spinbox.setValue(0.2)
        self.eye_norm_spinbox.valueChanged.connect(self.update_tracker) 

        # eye size
        self.eye_size_lo_label = QLabel(self)
        self.eye_size_lo_label.setText('min. eye size')

        self.eye_size_lo_spinbox = QDoubleSpinBox(self)
        self.eye_size_lo_spinbox.setRange(0,100)
        self.eye_size_lo_spinbox.setValue(0.8)
        self.eye_size_lo_spinbox.valueChanged.connect(self.update_tracker) 

        self.eye_size_hi_label = QLabel(self)
        self.eye_size_hi_label.setText('max. eye size')

        self.eye_size_hi_spinbox = QDoubleSpinBox(self)
        self.eye_size_hi_spinbox.setRange(0,100)
        self.eye_size_hi_spinbox.setValue(10)
        self.eye_size_hi_spinbox.valueChanged.connect(self.update_tracker) 

        # crop_dimension_mm 
        self.crop_dimension_x_mm_label = QLabel(self)
        self.crop_dimension_x_mm_label.setText('crop X (mm)')

        self.crop_dimension_x_spinbox = QDoubleSpinBox(self)
        self.crop_dimension_x_spinbox.setRange(0,3)
        self.crop_dimension_x_spinbox.setValue(1)
        self.crop_dimension_x_spinbox.valueChanged.connect(self.update_tracker)

        self.crop_dimension_y_mm_label = QLabel(self)
        self.crop_dimension_y_mm_label.setText('crop Y (mm)')

        self.crop_dimension_y_spinbox = QDoubleSpinBox(self)
        self.crop_dimension_y_spinbox.setRange(0,3)
        self.crop_dimension_y_spinbox.setValue(1.5)
        self.crop_dimension_y_spinbox.valueChanged.connect(self.update_tracker)

        # crop offset 
        self.crop_offset_mm_label = QLabel(self)
        self.crop_offset_mm_label.setText('Y offset eyes')

        self.crop_offset_mm_spinbox = QDoubleSpinBox(self)
        self.crop_offset_mm_spinbox.setRange(-5,5)
        self.crop_offset_mm_spinbox.setValue(-0.5)
        self.crop_offset_mm_spinbox.valueChanged.connect(self.update_tracker) 

        # ditance eye - midline
        self.dist_eye_midline_mm_label = QLabel(self)
        self.dist_eye_midline_mm_label.setText('eye - midline (mm)')

        self.dist_eye_midline_mm_spinbox = QDoubleSpinBox(self)
        self.dist_eye_midline_mm_spinbox.setRange(0,3)
        self.dist_eye_midline_mm_spinbox.setValue(0.1)
        self.dist_eye_midline_mm_spinbox.valueChanged.connect(self.update_tracker)

    def layout_components(self):
        row00 = QHBoxLayout()
        row00.addWidget(self.eye_gamma_label)
        row00.addWidget(self.eye_gamma_spinbox)

        row01 = QHBoxLayout()
        row01.addWidget(self.eye_contrast_label)
        row01.addWidget(self.eye_contrast_spinbox)

        row02 = QHBoxLayout()
        row02.addWidget(self.eye_norm_label)
        row03.addWidget(self.eye_norm_spinbox)

        row03 = QHBoxLayout()
        row03.addWidget(self.eye_size_lo_label)
        row03.addWidget(self.eye_size_lo_spinbox)

        row04 = QHBoxLayout()
        row04.addWidget(self.eye_size_hi_label)
        row04.addWidget(self.eye_size_hi_spinbox)

        row05 = QHBoxLayout()
        row05.addWidget(self.crop_dimension_x_mm_label)
        row05.addWidget(self.crop_dimension_x_spinbox)

        row06 = QHBoxLayout()
        row06.addWidget(self.crop_dimension_y_mm_label)
        row06.addWidget(self.crop_dimension_y_spinbox)

        row07 = QHBoxLayout()
        row07.addWidget(self.crop_offset_mm_label)
        row07.addWidget(self.crop_offset_mm_spinbox)

        row08 = QHBoxLayout()
        row08.addWidget(self.dist_eye_midline_mm_label)
        row08.addWidget(self.dist_eye_midline_mm_spinbox)    

        parameters = QVBoxLayout()
        parameters.addLayout(row00)
        parameters.addLayout(row01)
        parameters.addLayout(row02)
        parameters.addLayout(row03)
        parameters.addLayout(row04)
        parameters.addLayout(row05)
        parameters.addLayout(row06)
        parameters.addLayout(row07)
        parameters.addLayout(row08)

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.mask)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = EyesTrackerParamOverlay(
            pix_per_mm = self.pix_per_mm_spinbox.value(),
            eye_len_mm = 0.2,
            color_eye_left = (255,255,0),
            color_eye_right = (0,255,0),
            thickness = 2
        )
        tracker_param = EyesTrackerParamTracking(
            eye_gamma = self.eye_gamma_spinbox.value(),
            eye_contrast = self.eye_contrast_spinbox.value(),
            eye_norm = self.eye_norm_spinbox.value(),
            eye_size_lo_mm = self.eye_size_lo_spinbox.value(),
            eye_size_hi_mm = self.eye_size_hi_spinbox.value(),
            crop_offset_mm = self.crop_offset_mm_spinbox.value(),
            dist_eye_midline_mm = self.dist_eye_midline_mm_spinbox.value(), 
            crop_dimension_mm = (self.crop_dimension_x_spinbox.value(), self.crop_dimension_y_spinbox.value()),
        )
        self.tracker = EyesTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, heading: NDArray, centroid: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, heading, centroid)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()
