from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QHBoxLayout

class LabeledSpinBox(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = QLabel()
        self.spinbox = QSpinBox()
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def setText(self, text: str) -> None:
        self.label.setText(text)

    def setRange(self, lo: int, hi: int) -> None:
        self.spinbox.setRange(lo,hi)
    
    def setValue(self, val: int) -> None:
        self.spinbox.setValue(val)

    @property
    def valueChanged(self):
        return self.spinbox.valueChanged 

    def value(self) -> int:
        return self.spinbox.value()