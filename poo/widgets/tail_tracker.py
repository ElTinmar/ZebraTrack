from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from ..tracker.tail  import TailTracker, TailTrackerParamOverlay, TailTrackerParamTracking
from numpy.typing import NDArray
from typing import Optional
from .helper.ndarray_to_qpixmap import NDarray_to_QPixmap
from .custom_widgets.labeled_doublespinbox import LabeledDoubleSpinBox
from .custom_widgets.labeled_spinbox import LabeledSpinBox
    
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
        self.arc_angle_deg = LabeledDoubleSpinBox(self)
        self.arc_angle_deg.setText('tail max angle (deg)')
        self.arc_angle_deg.setRange(0,360)
        self.arc_angle_deg.setValue(120)
        self.arc_angle_deg.valueChanged.connect(self.update_tracker) 

        #ksize_blur_mm 
        self.ksize_blur_mm = LabeledDoubleSpinBox(self)
        self.ksize_blur_mm.setText('blur size (mm)')
        self.ksize_blur_mm.setRange(0,2)
        self.ksize_blur_mm.setValue(0.06)
        self.ksize_blur_mm.valueChanged.connect(self.update_tracker)
        
        # n_tail_points
        self.n_tail_points = LabeledSpinBox(self)
        self.n_tail_points.setText('#tail points')
        self.n_tail_points.setRange(0,100)
        self.n_tail_points.setValue(12)
        self.n_tail_points.valueChanged.connect(self.update_tracker)

        # tail_length_mm 
        self.tail_length_mm = LabeledDoubleSpinBox(self)
        self.tail_length_mm.setText('tail_length_mm')
        self.tail_length_mm.setRange(0,10)
        self.tail_length_mm.setValue(2.4)
        self.tail_length_mm.valueChanged.connect(self.update_tracker)

        # n_pts_arc
        self.n_pts_arc = LabeledSpinBox(self)
        self.n_pts_arc.setText('angle res.')
        self.n_pts_arc.setRange(0,100)
        self.n_pts_arc.setValue(20)
        self.n_pts_arc.valueChanged.connect(self.update_tracker)

        # n_pts_interp  
        self.n_pts_interp = LabeledSpinBox(self)
        self.n_pts_interp.setText('n_pts_interp')
        self.n_pts_interp.setRange(0,200)
        self.n_pts_interp.setValue(40)
        self.n_pts_interp.valueChanged.connect(self.update_tracker)

        # dist_swim_bladder_mm  
        self.dist_swim_bladder_mm = LabeledDoubleSpinBox(self)
        self.dist_swim_bladder_mm.setText('Offset tail Y (mm)')
        self.dist_swim_bladder_mm.setRange(0,3)
        self.dist_swim_bladder_mm.setValue(0.4)
        self.dist_swim_bladder_mm.valueChanged.connect(self.update_tracker)
        
    def layout_components(self):
        parameters = QVBoxLayout()
        parameters.addWidget(self.arc_angle_deg)
        parameters.addWidget(self.ksize_blur_mm)
        parameters.addWidget(self.n_tail_points)
        parameters.addWidget(self.tail_length_mm)
        parameters.addWidget(self.n_pts_arc)
        parameters.addWidget(self.n_pts_interp)
        parameters.addWidget(self.dist_swim_bladder_mm)    

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
            arc_angle_deg = self.arc_angle_deg.value(),
            ksize_blur_mm = self.ksize_blur_mm.value(),
            n_tail_points = self.n_tail_points.value(),
            tail_length_mm = self.tail_length_mm.value(),
            n_pts_arc = self.n_pts_arc.value(),
            n_pts_interp = self.n_pts_interp.value(), 
            dist_swim_bladder_mm = self.dist_swim_bladder_mm.value()
        )
        self.tracker = TailTracker(tracker_param, overlay_param)

    def set_image(self, image: NDArray, heading: NDArray, centroid: NDArray, offset = Optional[NDArray]):
        tracking = self.tracker.track(image, heading, centroid)
        overlay = self.tracker.overlay(image, tracking, offset)
        self.image.setPixmap(NDarray_to_QPixmap(image))
        self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
        self.update()