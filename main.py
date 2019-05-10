from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QComboBox, \
    QTableView, QMenu, QListWidgetItem, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QCursor
import sys
import os
import pandas as pd
import ui
import qtutils
import utils


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
        self.action_Open.triggered.connect(self.openOpen)
        self.files_tableWidget.setColumnWidth(0, 400)
        self.files_tableWidget.setColumnWidth(1, 60)
        self.files_tableWidget.setEditTriggers(QTableView.NoEditTriggers)
        self.options_tableWidget.setColumnWidth(0, 400)
        self.options_tableWidget.setColumnWidth(1, 60)
        self.options_tableWidget.setEditTriggers(QTableView.NoEditTriggers)
        self.plotQt = qtutils.PlotQt()
        self.xButton.clicked.connect(lambda: self.on_option_set('x'))
        self.yButton.clicked.connect(lambda: self.on_option_set('y'))
        self.cButton.clicked.connect(lambda: self.on_option_set('c'))

        self.data = []
        self.currentData = None
        self.currentDataBinder = utils.Binder(input_names=('c', 'x', 'y'))
        self.fileBinder = utils.Binder(input_names=('train', 'test'))
        self.supportedFormat = ['csv files (*.csv)', 'Microsoft Excel (*.xls *.xlsx)']
    
    def resizeEvent(self, event):
        # self.root_horizontal.resize(event.size().width(), event.size().height() - 25)
        pass
    
    def openHelp(self):
        self.helpWindow = HelpWindow()
        self.helpWindow.show()

    def openOpen(self):
        fname, format = QFileDialog.getOpenFileName(self, caption='打开文件',
                                                    filter=';;'.join(self.supportedFormat))
        if format == self.supportedFormat[0]:
            data = pd.read_csv(fname)
        elif format == self.supportedFormat[1]:
            data = pd.read_excel(fname)
        elif fname and format:
            QMessageBox.warning(self, '文件格式不正确', fname + '的文件格式不正确！', QMessageBox.Ok)
            return
        else:
            return
    
        self.data.append(data)
        self.action_insert_file(os.path.split(fname)[1])

    def action_insert_file(self, fileName):
        self.files_tableWidget.setRowCount(self.files_tableWidget.rowCount() + 1)
        self.files_tableWidget.setItem(self.files_tableWidget.rowCount() - 1, 0, QTableWidgetItem(fileName))
        comboBox = qtutils.OptionComboBox(fileName, ['', 'train', 'test'], self.on_file_inserted)
        self.files_tableWidget.setCellWidget(self.files_tableWidget.rowCount() - 1, 1, comboBox)

    @pyqtSlot(int, int)
    def on_file_dblclicked(self, i, j):
        self.currentData = self.data[i]
        self.options_tableWidget.setRowCount(0)
        for c in self.currentData.columns:
            self.currentDataBinder.output_names += (c,)
            self.options_tableWidget.setRowCount(self.options_tableWidget.rowCount() + 1)
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 0, QTableWidgetItem(c))
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 1, QTableWidgetItem())
        self.xButton.setEnabled(True)
        self.yButton.setEnabled(True)
        self.cButton.setEnabled(True)

    def on_option_set(self, option):
        selected_item: QTableWidgetItem = self.options_tableWidget.selectedItems()[0]
        self.currentDataBinder.connect(option, selected_item.text())
        data_x = self.currentDataBinder.infer('x')
        data_y = self.currentDataBinder.infer('y')
        data_c = self.currentDataBinder.infer('c')
        if data_x and data_y:
            if data_c:
                self.plotter.load(
                        QUrl.fromLocalFile(
                                self.plotQt.scatter(self.currentData[data_x], self.currentData[data_y],
                                                    self.currentData[data_c])
                        )
                )
            else:
                self.plotter.load(
                        QUrl.fromLocalFile(
                                self.plotQt.scatter(self.currentData[data_x], self.currentData[data_y])
                        )
                )
        for i in range(self.options_tableWidget.rowCount()):
            col: QTableWidgetItem = self.options_tableWidget.item(i, 0)
            op: QTableWidgetItem = self.options_tableWidget.item(i, 1)
            op.setText(self.currentDataBinder.refer(col.text()))

    def on_file_inserted(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
