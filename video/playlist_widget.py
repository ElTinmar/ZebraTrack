from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSpinBox, QSlider, QListWidgetItem, QListWidget, QFileDialog, QPushButton, QLineEdit, QComboBox, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from video.video_reader import OpenCV_VideoReader
from gui.helper.ndarray_to_qpixmap import NDarray_to_QPixmap
from gui.custom_widgets.labeled_slider_doublespinbox import LabeledSliderDoubleSpinBox
from gui.custom_widgets.labeled_slider_spinbox import LabeledSliderSpinBox

class PlaylistWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_reader = OpenCV_VideoReader()
        self.declare_components()
        self.layout_components()

        self.timer = QTimer()
        self.timer.timeout.connect(self.main)
        self.timer.setInterval(16)
        self.timer.start()

    def declare_components(self):

        # add zoom crop controls
        self.zoom = LabeledSliderDoubleSpinBox(self)
        self.zoom.setText('zoom')
        self.zoom.setValue(1.0)
        self.zoom.setRange(0.1, 5.0)
        self.zoom.valueChanged.connect(self.video_selected)

        self.left = LabeledSliderSpinBox(self)
        self.left.setText('left')
        self.left.setValue(0)
        self.left.valueChanged.connect(self.video_selected)

        self.bottom = LabeledSliderSpinBox(self)
        self.bottom.setText('bottom')
        self.bottom.setValue(0)
        self.bottom.valueChanged.connect(self.video_selected)

        self.width = LabeledSliderSpinBox(self)
        self.width.setText('width')
        self.width.setValue(100)
        self.width.valueChanged.connect(self.video_selected)

        self.height = LabeledSliderSpinBox(self)
        self.height.setText('height')
        self.height.setValue(100)
        self.height.valueChanged.connect(self.video_selected)

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

        crop_resize = QVBoxLayout()
        crop_resize.addWidget(self.zoom)
        crop_resize.addWidget(self.left)
        crop_resize.addWidget(self.bottom)
        crop_resize.addWidget(self.width)
        crop_resize.addWidget(self.height)
    
        playlist_control0 = QHBoxLayout()
        playlist_control0.addWidget(self.add_button)
        playlist_control0.addWidget(self.delete_button)

        playlist_control1 = QHBoxLayout()
        playlist_control1.addWidget(self.previous_button)
        playlist_control1.addWidget(self.next_button)

        controls = QVBoxLayout()
        controls.addLayout(crop_resize)
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
        frame = self.frame_slider.value()
        # TODO maybe chheck that video reader is opened
        self.video_reader.seek_to(frame)

    def add_video(self):
        file_name = QFileDialog.getOpenFileName(self, 'Select file')
        if file_name:
            list_item = QListWidgetItem(file_name[0])
            self.video_list.addItem(list_item)

    def delete_video(self):
        row = self.video_list.currentRow()
        if row:
            self.video_list.takeItem(row)

    def video_selected(self):
        current_item = self.video_list.currentItem()
        if current_item:
            filename = current_item.text()

            resize = self.zoom.value()
            left = self.left.value()
            bottom = self.bottom.value()
            width = self.width.value()
            height = self.height.value()
            
            self.video_reader.open_file(
                filename, 
                crop = (left, bottom, width, height),
                resize = resize 
            )

            num_frames = self.video_reader.get_number_of_frame()
            height_max = self.video_reader.get_height_max()
            width_max = self.video_reader.get_width_max()
            
            self.frame_slider.setMinimum(0)
            self.frame_slider.setMaximum(num_frames-1)
            self.frame_spinbox.setRange(0,num_frames-1)

            self.left.setRange(1, height_max-height)
            self.bottom.setRange(1, width_max-width)
            self.height.setRange(1, height_max-bottom)
            self.width.setRange(1, width_max-left)

    def previous_video(self):
        num_item = self.video_list.count()
        current_row = self.video_list.currentRow()
        previous_row = (current_row - 1) % num_item
        self.video_list.setCurrentRow(previous_row)

    def playpause_video(self):
        if self.playpause_button.isChecked():
            self.playpause_button.setText('pause')
        else:
            self.playpause_button.setText('play')

    def next_video(self):
        num_item = self.video_list.count()
        current_row = self.video_list.currentRow()
        next_row = (current_row + 1) % num_item
        self.video_list.setCurrentRow(next_row)

    def main(self):
        if self.playpause_button.isChecked():
            ret, image = self.video_reader.next_frame()
            frame_index = self.video_reader.get_current_frame_index()
            self.frame_slider.setValue(frame_index)
            self.frame_spinbox.setValue(frame_index)
            if ret:
                self.video_label.setPixmap(NDarray_to_QPixmap(image))


    