from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import ui


class HelpWindow(QMainWindow, ui.Ui_HelpWindow):
    def __init__(self, parent=None):
        super(HelpWindow, self).__init__(parent)
        self.setupUi(self)
    
    def resizeEvent(self, event):
        self.tabWidget.resize(event.size().width(), event.size().height() - 25)


class MainWindow(QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.actionClassifier_Help.triggered.connect(self.openHelp)

    """
    各种事件的处理
    """

    def resizeEvent(self, event):
        # self.root_horizontal.resize(event.size().width(), event.size().height() - 25)
        pass
    
    def openHelp(self):
        self.helpWindow = HelpWindow()
        self.helpWindow.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
