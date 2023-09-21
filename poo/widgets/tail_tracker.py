from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout
from tail import TailTracker, TailTrackerParamOverlay, TailTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from ndarray_to_qpixmap import NDarray_to_QPixmap
from labeled_doublespinbox import LabeledDoubleSpinBox
from labeled_spinbox import LabeledSpinBox
    
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