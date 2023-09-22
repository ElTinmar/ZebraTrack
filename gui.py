from widgets import BodyTrackerWidget, EyesTrackerWidget, TailTrackerWidget, MultiAnimalTrackerWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import os 
from background import *

class TrackerThreshold(QMainWindow):

    def __init__(self, reader: VideoReader, backgroundfile: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reader = reader
        self.backgroundfile = backgroundfile
        self.load_data()
        self.declare_components()
        self.layout_components()
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)
        self.timer.start()
        self.show()

    def load_data(self):
        if not os.path.exists(self.backgroundfile):
            self.reader.reset_reader()
            frames = sample_frames_evenly(self.reader, k = 250)
            self.bckg = background_model_mode(frames)
            np.save(self.backgroundfile, self.bckg)
        else:
            self.bckg = np.load(self.backgroundfile)

    def declare_components(self):
        self.multianimal_tracker_widget = MultiAnimalTrackerWidget(self)
        self.body_tracker_widget = BodyTrackerWidget(self)
        self.eyes_tracker_widget = EyesTrackerWidget(self)
        self.tail_tracker_widget = TailTrackerWidget(self)

    def layout_components(self):
        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.multianimal_tracker_widget)
        mainlayout.addWidget(self.body_tracker_widget)
        mainlayout.addWidget(self.eyes_tracker_widget)
        mainlayout.addWidget(self.tail_tracker_widget)
        widget = QWidget()
        widget.setLayout(mainlayout)
        self.setCentralWidget(widget)

    def loop(self):
        ret, image = self.videoreader.next_frame()
        if not ret:
            self.videoreader.reset_reader()
            return
        image_gray = im2single(im2gray(image))
        bckg_sub = image_gray - self.bckg

        # TODO add a mouse callback to select which fish you want to show for body/eye/tail

        self.multianimal_tracker_widget.set_image(bckg_sub)
        self.body_tracker_widget.set_image(bckg_sub)
        self.eyes_tracker_widget.set_image(bckg_sub)
        self.tail_tracker_widget.set_image(bckg_sub)