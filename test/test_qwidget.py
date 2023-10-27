import sys
from PyQt5.QtWidgets import QApplication
from tracker.assignment_widget import AssignmentWidget
from tracker.image_tools.roi_selector_widget import ROISelectorWidget
import numpy as np

image = np.random.randint(0,255,(1024,1024),dtype=np.uint8) 

app = QApplication(sys.argv)
window = ROISelectorWidget(image)
window.show()
sys.exit(app.exec())


