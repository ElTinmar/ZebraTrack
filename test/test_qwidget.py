import sys
from PyQt5.QtWidgets import QApplication
from tracker.assignment_widget import AssignmentWidget

app = QApplication(sys.argv)
window = AssignmentWidget()
window.show()
sys.exit(app.exec())


