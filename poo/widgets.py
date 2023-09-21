from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from body import BodyTracker, BodyTrackerParamOverlay, BodyTrackerParamTracking
from eyes import EyesTracker, EyesTrackerParamOverlay, EyesTrackerParamTracking
from tail import TailTracker, TailTrackerParamOverlay, TailTrackerParamTracking
from multi_animal import MultiAnimalTracker, MultiAnimalTrackerParamOverlay, MultiAnimalTrackerParamTracking
import numpy as np
from numpy.typing import NDArray
from typing import Optional

def NDarray_to_QPixmap(img: NDArray) -> QPixmap:
    if len(img.shape) == 2:
        img = np.dstack((img,img,img))
    
    h,w,ch = img.shape
    qimg = QImage(img.data, w, h, 3*w, QImage.Format_RGB888) 
    return QPixmap(qimg)

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

class TailTrackerWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = None
        self.declare_components()
        self.layout_components()

    def declare_components(self):
        self.image = QLabel(self)
        self.image_overlay = QLabel(self)
    
        # arc angle deg
        self.arc_angle_deg_label = QLabel(self)
        self.arc_angle_deg_label.setText('tail max angle (deg)')

        self.arc_angle_deg_spinbox = QDoubleSpinBox(self)
        self.arc_angle_deg_spinbox.setRange(0,360)
        self.arc_angle_deg_spinbox.setValue(120)
        self.arc_angle_deg_spinbox.valueChanged.connect(self.update_tracker) 

        #ksize_blur_mm 
        self.ksize_blur_mm_label = QLabel(self)
        self.ksize_blur_mm_label.setText('blur size (mm)')

        self.ksize_blur_mm_spinbox = QDoubleSpinBox(self)
        self.ksize_blur_mm_spinbox.setRange(0,2)
        self.ksize_blur_mm_spinbox.setValue(0.06)
        self.ksize_blur_mm_spinbox.valueChanged.connect(self.update_tracker)
        
        # n_tail_points
        self.n_tail_points_label = QLabel(self)
        self.n_tail_points_label.setText('#tail points')

        self.n_tail_points_spinbox = QSpinBox(self)
        self.n_tail_points_spinbox.setRange(0,100)
        self.n_tail_points_spinbox.setValue(12)
        self.n_tail_points_spinbox.valueChanged.connect(self.update_tracker)

        # tail_length_mm 
        self.tail_length_mm_label = QLabel(self)
        self.tail_length_mm_label.setText('tail_length_mm')

        self.tail_length_mm_spinbox = QDoubleSpinBox(self)
        self.tail_length_mm_spinbox.setRange(0,10)
        self.tail_length_mm_spinbox.setValue(2.4)
        self.tail_length_mm_spinbox.valueChanged.connect(self.update_tracker)

        # n_pts_arc
        self.n_pts_arc_label = QLabel(self)
        self.n_pts_arc_label.setText('angle res.')

        self.n_pts_arc_spinbox = QSpinBox(self)
        self.n_pts_arc_spinbox.setRange(0,100)
        self.n_pts_arc_spinbox.setValue(20)
        self.n_pts_arc_spinbox.valueChanged.connect(self.update_tracker)

        # n_pts_interp  
        self.n_pts_interp_label = QLabel(self)
        self.n_pts_interp_label.setText('n_pts_interp')

        self.n_pts_interp_spinbox = QSpinBox(self)
        self.n_pts_interp_spinbox.setRange(0,200)
        self.n_pts_interp_spinbox.setValue(40)
        self.n_pts_interp_spinbox.valueChanged.connect(self.update_tracker)

        # dist_swim_bladder_mm_label  
        self.dist_swim_bladder_mm_label = QLabel(self)
        self.dist_swim_bladder_mm_label.setText('Offset tail Y (mm)')

        self.dist_swim_bladder_mm_spinbox = QDoubleSpinBox(self)
        self.dist_swim_bladder_mm_spinbox.setRange(0,3)
        self.dist_swim_bladder_mm_spinbox.setValue(0.4)
        self.dist_swim_bladder_mm_spinbox.valueChanged.connect(self.update_tracker)
        

    def layout_components(self):
        row00 = QHBoxLayout()
        row00.addWidget(self.arc_angle_deg_label)
        row00.addWidget(self.arc_angle_deg_spinbox)

        row01 = QHBoxLayout()
        row01.addWidget(self.ksize_blur_mm_label)
        row01.addWidget(self.ksize_blur_mm_spinbox)

        row02 = QHBoxLayout()
        row02.addWidget(self.n_tail_points_label)
        row02.addWidget(self.n_tail_points_spinbox)

        row03 = QHBoxLayout()
        row03.addWidget(self.tail_length_mm_label)
        row03.addWidget(self.tail_length_mm_spinbox)

        row04 = QHBoxLayout()
        row04.addWidget(self.n_pts_arc_label)
        row04.addWidget(self.n_pts_arc_spinbox)

        row05 = QHBoxLayout()
        row05.addWidget(self.n_pts_interp_label)
        row05.addWidget(self.n_pts_interp_spinbox)

        row06 = QHBoxLayout()
        row06.addWidget(self.dist_swim_bladder_mm_label)
        row06.addWidget(self.dist_swim_bladder_mm_spinbox)    

        parameters = QVBoxLayout()
        parameters.addLayout(row00)
        parameters.addLayout(row01)
        parameters.addLayout(row02)
        parameters.addLayout(row03)
        parameters.addLayout(row04)
        parameters.addLayout(row05)
        parameters.addLayout(row06)

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = TailTrackerParamOverlay(
            color_tail = (255, 128, 128),
            thickness = 2
        )
        tracker_param = TailTrackerParamTracking(
            arc_angle_deg = self.arc_angle_deg_spinbox.value(),
            ksize_blur_mm = self.ksize_blur_mm_spinbox.value(),
            n_tail_points = self.n_tail_points_spinbox.value(),
            tail_length_mm = self.tail_length_mm_spinbox.value(),
            n_pts_arc = self.n_pts_arc_spinbox.value(),
            n_pts_interp = self.n_pts_interp_spinbox.value(), 
            dist_swim_bladder_mm = self.dist_swim_bladder_mm_spinbox.value()
        )
        self.tracker = TailTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, heading: NDArray, centroid: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, heading, centroid)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()

class MultiAnimalTrackerWidget(QWidget):
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


        # pad value  
        self.pad_value_mm_label = QLabel(self)
        self.pad_value_mm_label.setText('Bbox size (mm)')

        self.pad_value_mm_spinbox = QDoubleSpinBox(self)
        self.pad_value_mm_spinbox.setRange(0,10)
        self.pad_value_mm_spinbox.setValue(2.5)
        self.pad_value_mm_spinbox.valueChanged.connect(self.update_tracker)

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

        row08 = QHBoxLayout()
        row08.addWidget(self.pad_value_mm_label)
        row08.addWidget(self.pad_value_mm_spinbox)    

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
        overlay_param = MultiAnimalTrackerParamOverlay(

        )
        tracker_param = MultiAnimalTrackerParamTracking(
            pix_per_mm = self.pix_per_mm_spinbox.value(),
            body_intensity = self.body_intensity_spinbox.value(),
            min_body_size_mm = self.min_body_size_mm_spinbox.value(),
            max_body_size_mm = self.max_body_size_mm_spinbox.value(),
            min_body_length_mm = self.min_body_length_mm_spinbox.value(),
            max_body_length_mm = self.max_body_length_mm_spinbox.value(),
            min_body_width_mm = self.min_body_width_mm_spinbox.value(),
            max_body_width_mm = self.max_body_width_mm_spinbox.value(),
            pad_value_mm = self.pad_value_mm_spinbox.value(),
        )
        self.tracker = MultiAnimalTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray):
        tracking = self.tracker.track(image)
        overlay = self.tracker.overlay(image, tracking)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()