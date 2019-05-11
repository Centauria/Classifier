from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QComboBox, \
    QTableView, QMenu, QListWidgetItem, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QUrl, QModelIndex
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
        """Initialize menus"""
        self.actionClassifier_Help.triggered.connect(self.open_help_window)
        self.action_Open.triggered.connect(self.open_open_dialog)
        self.actionset_x.triggered.connect(lambda trig: self.on_option_set('x', trig))
        self.actionset_y.triggered.connect(lambda trig: self.on_option_set('y', trig))
        self.actionset_c.triggered.connect(lambda trig: self.on_option_set('c', trig))
        self.actionset_train.triggered.connect(lambda trig: self.on_file_set('train', trig))
        self.actionset_test.triggered.connect(lambda trig: self.on_file_set('test', trig))
        """Initialize widgets"""
        self.files_tableWidget.setColumnWidth(0, 400)
        self.files_tableWidget.setColumnWidth(1, 60)
        self.files_tableWidget.setEditTriggers(QTableView.NoEditTriggers)
        self.files_tableWidget.itemSelectionChanged.connect(self.on_file_selected)
        self.options_tableWidget.setColumnWidth(0, 400)
        self.options_tableWidget.setColumnWidth(1, 60)
        self.options_tableWidget.setEditTriggers(QTableView.NoEditTriggers)
        self.options_tableWidget.itemSelectionChanged.connect(self.on_column_selected)
        self.plotQt = qtutils.PlotQt()
        self.xButton.clicked.connect(lambda: self.actionset_x.trigger())
        self.yButton.clicked.connect(lambda: self.actionset_y.trigger())
        self.cButton.clicked.connect(lambda: self.actionset_c.trigger())
        """Initialize data"""
        self.data = []
        self.currentData = None
        self.currentDataBinder = utils.Binder(input_names=('c', 'x', 'y'))
        self.fileBinder = utils.Binder(input_names=('train', 'test'))
        self.currentTrace = []
        self.supportedFormat = ['csv files (*.csv)', 'Microsoft Excel (*.xls *.xlsx)']
    
    def resizeEvent(self, event):
        # self.root_horizontal.resize(event.size().width(), event.size().height() - 25)
        pass

    def open_help_window(self):
        self.helpWindow = HelpWindow()
        self.helpWindow.show()

    def open_open_dialog(self):
        fname, format = QFileDialog.getOpenFileName(self, caption='打开文件', filter=';;'.join(self.supportedFormat))
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

    def action_insert_file(self, file_name):
        self.fileBinder.output_names += (file_name,)
        self.files_tableWidget.setRowCount(self.files_tableWidget.rowCount() + 1)
        self.files_tableWidget.setItem(self.files_tableWidget.rowCount() - 1, 0, QTableWidgetItem(file_name))
        self.files_tableWidget.setItem(self.files_tableWidget.rowCount() - 1, 1, QTableWidgetItem())
    
    @pyqtSlot(int, int)
    def on_file_dblclicked(self, i, j):
        self.currentData = self.data[i]
        self.options_tableWidget.setRowCount(0)
        for c in self.currentData.columns:
            self.currentDataBinder.output_names += (c,)
            self.options_tableWidget.setRowCount(self.options_tableWidget.rowCount() + 1)
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 0, QTableWidgetItem(c))
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 1, QTableWidgetItem())

    def on_file_selected(self):
        have_selected = len(self.files_tableWidget.selectedItems()) != 0
        self.menuset_current_file_as.setEnabled(have_selected)
        if have_selected:
            selected_index: QModelIndex = self.files_tableWidget.selectedIndexes()[0]
            selected_item: QTableWidgetItem = self.files_tableWidget.item(selected_index.row(), 0)
            option = self.fileBinder.refer(selected_item.text())
            self.set_file_menu_status(option)

    def on_column_selected(self):
        have_selected = len(self.options_tableWidget.selectedItems()) != 0
        self.menuset_current_item_as.setEnabled(have_selected)
        self.xButton.setEnabled(have_selected)
        self.yButton.setEnabled(have_selected)
        self.cButton.setEnabled(have_selected)
        if have_selected:
            selected_index: QModelIndex = self.options_tableWidget.selectedIndexes()[0]
            selected_item: QTableWidgetItem = self.options_tableWidget.item(selected_index.row(), 0)
            option = self.currentDataBinder.refer(selected_item.text())
            self.set_column_menu_status(option)

    def on_file_set(self, option, trig):
        selected_index: QModelIndex = self.files_tableWidget.selectedIndexes()[0]
        selected_item: QTableWidgetItem = self.files_tableWidget.item(selected_index.row(), 0)
        if trig:
            self.fileBinder.connect(option, selected_item.text())
        else:
            self.fileBinder.disconnect(option, selected_item.text())
        for i in range(self.files_tableWidget.rowCount()):
            col: QTableWidgetItem = self.files_tableWidget.item(i, 0)
            op: QTableWidgetItem = self.files_tableWidget.item(i, 1)
            op.setText(self.fileBinder.refer(col.text()))
        option = self.fileBinder.refer(selected_item.text())
        self.set_file_menu_status(option)

    def on_option_set(self, option, trig):
        selected_index: QModelIndex = self.options_tableWidget.selectedIndexes()[0]
        selected_item: QTableWidgetItem = self.options_tableWidget.item(selected_index.row(), 0)
        if trig:
            self.currentDataBinder.connect(option, selected_item.text())
        else:
            self.currentDataBinder.disconnect(option, selected_item.text())
        data_x = self.currentDataBinder.infer('x')
        data_y = self.currentDataBinder.infer('y')
        data_c = self.currentDataBinder.infer('c')
        if data_x and data_y:
            if data_c:
                html_path, self.currentTrace = self.plotQt.scatter(self.currentData[data_x], self.currentData[data_y],
                                                                   self.currentData[data_c])
                self.plotter.load(QUrl.fromLocalFile(html_path))
            else:
                html_path, self.currentTrace = self.plotQt.scatter(self.currentData[data_x], self.currentData[data_y])
                self.plotter.load(QUrl.fromLocalFile(html_path))
        for i in range(self.options_tableWidget.rowCount()):
            col: QTableWidgetItem = self.options_tableWidget.item(i, 0)
            op: QTableWidgetItem = self.options_tableWidget.item(i, 1)
            op.setText(self.currentDataBinder.refer(col.text()))
        option = self.currentDataBinder.refer(selected_item.text())
        self.set_column_menu_status(option)

    def set_file_menu_status(self, option):
        if option == 'train':
            self.actionset_train.setChecked(True)
            self.actionset_test.setChecked(False)
        elif option == 'test':
            self.actionset_train.setChecked(False)
            self.actionset_test.setChecked(True)
        else:
            self.actionset_train.setChecked(False)
            self.actionset_test.setChecked(False)

    def set_column_menu_status(self, option):
        if option == 'x':
            self.actionset_x.setChecked(True)
            self.actionset_y.setChecked(False)
            self.actionset_c.setChecked(False)
        elif option == 'y':
            self.actionset_x.setChecked(False)
            self.actionset_y.setChecked(True)
            self.actionset_c.setChecked(False)
        elif option == 'c':
            self.actionset_x.setChecked(False)
            self.actionset_y.setChecked(False)
            self.actionset_c.setChecked(True)
        else:
            self.actionset_x.setChecked(False)
            self.actionset_y.setChecked(False)
            self.actionset_c.setChecked(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
