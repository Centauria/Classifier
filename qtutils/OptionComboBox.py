from PyQt5.QtWidgets import QComboBox
import utils


class OptionComboBox(QComboBox):
    def __init__(self, column, items, on_option_changed, parent=None):
        super(OptionComboBox, self).__init__(parent)
        self.column_name = column
        self.addItems(items)
        self.binder = utils.Binder()
        for i in range(len(items)):
            self.binder.connect(i, items[i])
        self.currentIndexChanged.connect(lambda index: on_option_changed(self.currentText(), self.column_name))
