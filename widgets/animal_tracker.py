from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from trackers.animal import AnimalTracker, AnimalTrackerParamOverlay, AnimalTrackerParamTracking
from numpy.typing import NDArray
from .helper.ndarray_to_qpixmap import NDarray_to_QPixmap
from .custom_widgets.labeled_doublespinbox import LabeledDoubleSpinBox

class AnimalTrackerWidget(QWidget):
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
        self.pix_per_mm.setSingleStep(1.0)
        self.pix_per_mm.valueChanged.connect(self.update_tracker)

        # pix per mm
        self.target_pix_per_mm = LabeledDoubleSpinBox(self)
        self.target_pix_per_mm.setText('target pixels / mm')
        self.target_pix_per_mm.setRange(0,1000)
        self.target_pix_per_mm.setValue(7.5)
        self.target_pix_per_mm.setSingleStep(0.5)
        self.target_pix_per_mm.valueChanged.connect(self.update_tracker)

        # body intensity
        self.body_intensity = LabeledDoubleSpinBox(self)
        self.body_intensity.setText('body intensity')
        self.body_intensity.setRange(0,1)
        self.body_intensity.setValue(0.08)
        self.body_intensity.setSingleStep(0.01)
        self.body_intensity.valueChanged.connect(self.update_tracker)

        # body size
        self.min_body_size_mm = LabeledDoubleSpinBox(self)
        self.min_body_size_mm.setText('min body size (mm)')
        self.min_body_size_mm.setRange(0,1000)
        self.min_body_size_mm.setValue(2.0)
        self.min_body_size_mm.setSingleStep(0.25)
        self.min_body_size_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_size_mm = LabeledDoubleSpinBox(self)
        self.max_body_size_mm.setText('max body size (mm)')
        self.max_body_size_mm.setRange(0,1000)
        self.max_body_size_mm.setValue(30.0)
        self.max_body_size_mm.setSingleStep(0.5)
        self.max_body_size_mm.valueChanged.connect(self.update_tracker)

        # body length
        self.min_body_length_mm = LabeledDoubleSpinBox(self)
        self.min_body_length_mm.setText('min body length (mm)')
        self.min_body_length_mm.setRange(0,100)
        self.min_body_length_mm.setValue(2.0)
        self.min_body_length_mm.setSingleStep(0.25)
        self.min_body_length_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_length_mm = LabeledDoubleSpinBox(self)
        self.max_body_length_mm.setText('max body length (mm)')
        self.max_body_length_mm.setRange(0,100)
        self.max_body_length_mm.setValue(6.0)
        self.max_body_length_mm.setSingleStep(0.25)
        self.max_body_length_mm.valueChanged.connect(self.update_tracker)

        # body width
        self.min_body_width_mm = LabeledDoubleSpinBox(self)
        self.min_body_width_mm.setText('min body width (mm)')
        self.min_body_width_mm.setRange(0,100)
        self.min_body_width_mm.setValue(0.4)
        self.min_body_width_mm.setSingleStep(0.05)
        self.min_body_width_mm.valueChanged.connect(self.update_tracker)

        #
        self.max_body_width_mm = LabeledDoubleSpinBox(self)
        self.max_body_width_mm.setText('max body width (mm)')
        self.max_body_width_mm.setRange(0,100)
        self.max_body_width_mm.setValue(1.2)
        self.max_body_width_mm.setSingleStep(0.05)
        self.max_body_width_mm.valueChanged.connect(self.update_tracker)

        # pad value  
        self.pad_value_mm = LabeledDoubleSpinBox(self)
        self.pad_value_mm.setText('Bbox size (mm)')
        self.pad_value_mm.setRange(0,10)
        self.pad_value_mm.setValue(2.5)
        self.pad_value_mm.setSingleStep(0.1)
        self.pad_value_mm.valueChanged.connect(self.update_tracker)

    def layout_components(self):

        parameters = QVBoxLayout()
        parameters.addWidget(self.pix_per_mm)
        parameters.addWidget(self.target_pix_per_mm)
        parameters.addWidget(self.body_intensity)
        parameters.addWidget(self.min_body_size_mm)
        parameters.addWidget(self.max_body_size_mm)
        parameters.addWidget(self.min_body_length_mm)
        parameters.addWidget(self.max_body_length_mm)
        parameters.addWidget(self.min_body_width_mm)
        parameters.addWidget(self.max_body_width_mm)
        parameters.addWidget(self.pad_value_mm)    

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.image)
        mainlayout.addWidget(self.mask)
        mainlayout.addWidget(self.image_overlay)
        mainlayout.addLayout(parameters)

        self.setLayout(mainlayout)

    def update_tracker(self):
        overlay_param = AnimalTrackerParamOverlay(

        )
        tracker_param = AnimalTrackerParamTracking(
            pix_per_mm = self.pix_per_mm.value(),
            target_pix_per_mm = self.target_pix_per_mm.value(),
            body_intensity = self.body_intensity.value(),
            min_body_size_mm = self.min_body_size_mm.value(),
            max_body_size_mm = self.max_body_size_mm.value(),
            min_body_length_mm = self.min_body_length_mm.value(),
            max_body_length_mm = self.max_body_length_mm.value(),
            min_body_width_mm = self.min_body_width_mm.value(),
            max_body_width_mm = self.max_body_width_mm.value(),
            pad_value_mm = self.pad_value_mm.value(),
        )
        self.tracker = AnimalTracker(tracker_param, overlay_param)

    def track(self, image: NDArray):
        tracking = self.tracker.track(image)
        self.display(tracking)

    def display(self, tracking):
        if tracking is not None:
            overlay = self.tracker.overlay_local(tracking)
            self.image.setPixmap(NDarray_to_QPixmap(tracking.image))
            self.mask.setPixmap(NDarray_to_QPixmap(tracking.mask))
            self.image_overlay.setPixmap(NDarray_to_QPixmap(overlay))
            self.update()