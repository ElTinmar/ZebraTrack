import sys
from PyQt5.QtWidgets import QApplication
from image_tools import ROISelectorDialog, ROISelectorWidget
import numpy as np

image = np.random.randint(0,255,(1024,1024),dtype=np.uint8) 

# test dialog
app = QApplication(sys.argv)
window = ROISelectorDialog(image)
while not window.exec_():
    pass
print(window.ROIs)
    

