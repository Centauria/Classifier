from PyQt5.QtWidgets import QPushButton
import utils


class OptionPushButton(QPushButton):
    def __init__(self, column, on_option_set, parent=None):
        super(OptionPushButton, self).__init__(parent)
        self.column_name = column
        self.currentIndexChanged.connect(lambda index: on_option_set(self.column_name))
