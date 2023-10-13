import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication
from video.background_widget import BackgroundSubtractorWidget 

app = QApplication(sys.argv)
ex = BackgroundSubtractorWidget()
ex.show()
sys.exit(app.exec_())