import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication
from video.playlist_widget import PlaylistWidget 
from gui.custom_widgets.labeled_editline_openfile import FileOpenLabeledEditButton

app = QApplication(sys.argv)
ex = PlaylistWidget()
ex.show()
sys.exit(app.exec_())