import sys
from PyQt5.QtWidgets import QApplication
from tracker.assignment_widget import AssignmentWidget
from tracker.image_tools.roi_selector_widget import ROISelectorDialog, ROISelectorWidget
import numpy as np

image = np.random.randint(0,255,(1024,1024),dtype=np.uint8) 

# test widget
#app = QApplication(sys.argv)
#window = ROISelectorWidget(image)
#window.show()
#sys.exit(app.exec())

# test dialog
app = QApplication(sys.argv)
window = ROISelectorDialog(image)
while not window.exec_():
    pass
print(window.ROIs)
    

