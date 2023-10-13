from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSpinBox, QSlider, QListWidget, QFileDialog, QPushButton, QLineEdit, QComboBox, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from video.video_reader import OpenCV_VideoReader

class PlaylistWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_reader = None
        self.declare_components()
        self.layout_components()

        self.timer = QTimer()
        self.timer.timeout.connect(self.main)
        self.timer.setInterval(33)
        self.timer.start()

    def declare_components(self):

        self.add_button = QPushButton('add', self)
        self.add_button.clicked.connect(self.add_video)

        self.delete_button = QPushButton('delete', self)
        self.delete_button.clicked.connect(self.delete_video)

        self.video_list = QListWidget(self)
        self.video_list.currentRowChanged.connect(self.video_selected)

        self.previous_button = QPushButton('prev', self)
        self.previous_button.clicked.connect(self.previous_video)

        self.next_button = QPushButton('next', self)
        self.previous_button.clicked.connect(self.next_video)

        self.video_label = QLabel(self)

        self.playpause_button = QPushButton('play', self)
        self.playpause_button.setCheckable(True)
        self.playpause_button.clicked.connect(self.playpause_video)

        self.frame_slider = QSlider(Qt.Horizontal, self)
        self.frame_slider.valueChanged.connect(self.frame_changed_slider)

        self.frame_spinbox = QSpinBox(self)
        self.frame_spinbox.valueChanged.connect(self.frame_changed_spinbox)

    def layout_components(self):

        playlist_control0 = QHBoxLayout()
        playlist_control0.addWidget(self.add_button)
        playlist_control0.addWidget(self.delete_button)

        playlist_control1 = QHBoxLayout()
        playlist_control1.addWidget(self.previous_button)
        playlist_control1.addWidget(self.next_button)

        controls = QVBoxLayout()
        controls.addLayout(playlist_control0)
        controls.addWidget(self.video_list)
        controls.addLayout(playlist_control1)

        video_controls = QHBoxLayout()
        video_controls.addWidget(self.playpause_button)
        video_controls.addWidget(self.frame_slider)
        video_controls.addWidget(self.frame_spinbox)
        
        video_display = QVBoxLayout()
        video_display.addWidget(self.video_label)
        video_display.addLayout(video_controls)

        mainlayout = QHBoxLayout(self)
        mainlayout.addLayout(controls)
        mainlayout.addLayout(video_display)

    def frame_changed_slider(self):
        self.frame_spinbox.setValue(self.frame_slider.value())
        self.frame_changed()

    def frame_changed_spinbox(self):
        self.frame_slider.setValue(self.frame_spinbox.value())
        self.frame_changed()
        
    def frame_changed(self):
        pass

    def add_video(self):
        pass

    def delete_video(self):
        pass

    def video_selected(self):
        pass
    
    def previous_video(self):
        pass

    def playpause_video(self):
        if self.playpause_button.isChecked():
            self.playpause_button.setText('pause')
        else:
            #pause
            self.playpause_button.setText('play')

    def next_video(self):
        pass

    def main(self):
        pass

    