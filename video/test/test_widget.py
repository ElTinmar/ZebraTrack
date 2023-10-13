import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ..background_widget import BackgroundSubtractorWidget 

app = QApplication(sys.argv)
ex = BackgroundSubtractorWidget()
ex.show()
sys.exit(app.exec_())