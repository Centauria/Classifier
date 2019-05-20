from PyQt5.QtWidgets import QDialog, QComboBox, QFormLayout, QHBoxLayout, QLabel, QSlider, QLineEdit
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt


class ParameterDialog(QDialog):
    ComboBox = 0
    IntSlider = 1
    FloatSlider = 2
    
    def __init__(self, parameter_dict: dict, parent=None):
        super(ParameterDialog, self).__init__(parent)
        self.setWindowTitle('Parameters')
        self.setWindowModality(Qt.NonModal)
        self.parameters = parameter_dict
        self.ui()
    
    def ui(self):
        layout = QFormLayout(self)
        for k, v in self.parameters.items():
            if v['kind'] == ParameterDialog.ComboBox:
                comboBox = QComboBox()
                comboBox.addItems(v['items'])
                layout.addRow(k, comboBox)
            elif v['kind'] == ParameterDialog.FloatSlider:
                f = lambda n: v['min'] + n / 100 * (v['max'] - v['min'])
                g = lambda x: int((x - v['min']) / (v['max'] - v['min']) * 100)
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(100)
                slider.setSingleStep(1)
                slider.setValue(g(v['init']))
                le = QLineEdit()
                le.setPlaceholderText(v['init'])
                dv = QDoubleValidator(self)
                dv.setRange(v['min'], v['max'])
                dv.setNotation(QDoubleValidator.StandardNotation)
                dv.setDecimals(2)
                le.setValidator(dv)
                # slider.valueChanged.connect(lambda n: le.setText(f(n)))
                # le.textChanged.connect(lambda x: slider.setValue(g(x)))
                hlayout = QHBoxLayout()
                hlayout.addWidget(slider, alignment=Qt.AlignLeft)
                hlayout.addWidget(le, alignment=Qt.AlignRight)
                layout.addRow(k, hlayout)
        self.setLayout(layout)
