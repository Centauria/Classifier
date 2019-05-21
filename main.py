from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox, QTableWidgetItem, \
    QComboBox, QCheckBox, QTableView, QMenu, QListWidgetItem, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QUrl, QModelIndex
from PyQt5.QtGui import QCursor
import sys
import os
import pandas as pd
import numpy as np
import ui
import qtutils
import utils
import classifier


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
        self.xButton.clicked.connect(self.actionset_x.trigger)
        self.yButton.clicked.connect(self.actionset_y.trigger)
        self.cButton.clicked.connect(self.actionset_c.trigger)
        self.classifier_property_pushButton.clicked.connect(self.set_property)
        self.create_classifier_pushButton.clicked.connect(self.create_classifier)
        self.show_test_pushButton.clicked.connect(self.evaluate_classifier)
        self.train_checkBox.toggled.connect(lambda toggled: self.on_checkBoxes_toggled(self.train_checkBox, toggled))
        self.test_checkBox.toggled.connect(lambda toggled: self.on_checkBoxes_toggled(self.test_checkBox, toggled))
        self.result_checkBox.toggled.connect(lambda toggled: self.on_checkBoxes_toggled(self.result_checkBox, toggled))
        """Initialize data"""
        self.data = dict()
        self.currentData = None
        self.currentDataBinder = utils.Binder(input_names=('c', 'x', 'y'))
        self.currentTestData = None
        self.currentTestResult = None
        self.currentTestAccuracy = None
        self.fileBinder = utils.Binder(input_names=('train', 'test'))
        self.currentTrace = []
        self.supportedFormat = ['csv files (*.csv)', 'Microsoft Excel (*.xls *.xlsx)']
        self.classifier: classifier.AbstractClassifier = None
        self.classifier_property = ('exp', 1.0)
        self.show_train_data = True
        self.show_test_data = False
        self.show_result_data = False
    
    def resizeEvent(self, event):
        # self.root_horizontal.resize(event.size().width(), event.size().height() - 25)
        pass

    def open_help_window(self):
        self.helpWindow = HelpWindow()
        self.helpWindow.show()

    def open_open_dialog(self):
        self.statusbar.showMessage('正在选择文件……')
        fname, format = QFileDialog.getOpenFileName(self, caption='打开文件', filter=';;'.join(self.supportedFormat))
        if format == self.supportedFormat[0]:
            self.statusbar.showMessage('正在打开文件……')
            data = pd.read_csv(fname)
        elif format == self.supportedFormat[1]:
            self.statusbar.showMessage('正在打开文件……')
            data = pd.read_excel(fname)
        elif fname and format:
            QMessageBox.warning(self, '文件格式不正确', fname + '的文件格式不正确！', QMessageBox.Ok)
            self.statusbar.clearMessage()
            return
        else:
            self.statusbar.clearMessage()
            return

        file_name = os.path.split(fname)[1]
        self.data[file_name] = data
        self.insert_file(file_name)
        self.statusbar.clearMessage()

    def insert_file(self, file_name):
        self.fileBinder.output_names += (file_name,)
        self.files_tableWidget.setRowCount(self.files_tableWidget.rowCount() + 1)
        self.files_tableWidget.setItem(self.files_tableWidget.rowCount() - 1, 0, QTableWidgetItem(file_name))
        self.files_tableWidget.setItem(self.files_tableWidget.rowCount() - 1, 1, QTableWidgetItem())
    
    @pyqtSlot(int, int)
    def on_file_dblclicked(self, i, j):
        self.statusbar.showMessage('正在加载文件……')
        current_index = list(self.data.keys())[i]
        self.currentData = self.data[current_index]
        self.options_tableWidget.setRowCount(0)
        self.currentDataBinder.output_names = self.currentData.columns
        # self.actionset_train.trigger()
        for c in self.currentData.columns:
            self.options_tableWidget.setRowCount(self.options_tableWidget.rowCount() + 1)
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 0, QTableWidgetItem(c))
            self.options_tableWidget.setItem(self.options_tableWidget.rowCount() - 1, 1, QTableWidgetItem())
        self.statusbar.clearMessage()

    def on_checkBoxes_toggled(self, cb: QCheckBox, toggled):
        if cb == self.train_checkBox:
            self.show_train_data = toggled
        elif cb == self.test_checkBox:
            self.show_test_data = toggled
        elif cb == self.result_checkBox:
            self.show_result_data = toggled
        self.plot_refresh()
    
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
            if option == 'train':
                self.currentData = self.data[selected_item.text()]
            elif option == 'test':
                self.currentTestData = self.data[selected_item.text()]
        else:
            self.fileBinder.disconnect(option, selected_item.text())
            if option == 'train':
                self.currentData = None
            elif option == 'test':
                self.currentTestData = None
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
        self.plot_refresh()
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

    def set_property(self):
        func, ok = QInputDialog.getItem(self, 'Parameters', '势函数', ['exp', 'cauchy'])
        if ok:
            alpha, ok = QInputDialog.getDouble(self, 'Parameters', 'alpha', 1.0)
            if ok:
                self.classifier_property = (func, alpha)

    def plot_new(self, x, y, c=None, marker=None):
        html_path, self.currentTrace = self.plotQt.scatter(x, y, c, marker=marker)
        self.plotter.load(QUrl.fromLocalFile(html_path))

    def plot_append(self, x, y, c=None, marker=None):
        html_path, self.currentTrace = self.plotQt.scatter(x, y, c, traces=self.currentTrace, marker=marker)
        self.plotter.load(QUrl.fromLocalFile(html_path))

    def plot_clear(self):
        self.plotter.setHtml('')

    def plot_refresh(self):
        self.statusbar.showMessage('正在自动绘图……')
        data_x = self.currentDataBinder.infer('x')
        data_y = self.currentDataBinder.infer('y')
        data_c = self.currentDataBinder.infer('c')
        self.plot_clear()
        self.currentTrace = None
        if data_x and data_y:
            if self.show_train_data:
                if data_c:
                    self.plot_append(
                            self.currentData[data_x],
                            self.currentData[data_y],
                            self.currentData[data_c],
                            marker=dict(
                                    size=3
                            )
                    )
                else:
                    self.plot_append(
                            self.currentData[data_x],
                            self.currentData[data_y],
                            marker=dict(
                                    size=3
                            )
                    )
            if self.show_test_data:
                if self.currentTestData is not None:
                    if data_c:
                        self.plot_append(
                                self.currentTestData[data_x],
                                self.currentTestData[data_y],
                                self.currentTestData[data_c],
                                marker=dict(
                                        size=6,
                                        symbol='circle-open'
                                )
                        )
                    else:
                        self.plot_append(
                                self.currentTestData[data_x],
                                self.currentTestData[data_y],
                                marker=dict(
                                        size=6,
                                        symbol='circle-open'
                                )
                        )
            if self.show_result_data:
                if self.currentTestResult is not None:
                    test_result = self.currentTestData[[data_x, data_y]]
                    test_result.loc[:, data_c] = self.currentTestResult
                    if data_c:
                        self.plot_append(
                                test_result[data_x],
                                test_result[data_y],
                                test_result[data_c],
                                marker=dict(
                                        size=6,
                                        symbol='cross'
                                )
                        )
                    else:
                        self.plot_append(
                                test_result[data_x],
                                test_result[data_y],
                                marker=dict(
                                        size=6,
                                        symbol='cross'
                                )
                        )
        self.statusbar.clearMessage()

    def create_classifier(self):
        self.statusbar.showMessage('正在创建分类器……')
        if not self.currentDataBinder.infer('c'):
            QMessageBox.warning(self, '警告', '请指定输入数据的类别列！', QMessageBox.Ok)
            self.statusbar.clearMessage()
            return
        # index = list(set(self.currentData.columns) - {self.currentDataBinder.infer('c')})
        index = list(self.currentData.columns).copy()
        index.remove(self.currentDataBinder.infer('c'))
        func, alpha = self.classifier_property
        if func == 'exp':
            self.classifier = classifier.PotentialClassifier(
                    self.currentData[index],
                    self.currentData[self.currentDataBinder.infer('c')],
                    potential_function=classifier.PotentialFunctions.exponential(alpha)
            )
        elif func == 'cauchy':
            self.classifier = classifier.PotentialClassifier(
                    self.currentData[index],
                    self.currentData[self.currentDataBinder.infer('c')],
                    potential_function=classifier.PotentialFunctions.cauchy(alpha)
            )
        QMessageBox.information(self, '提示', '设置成功！', QMessageBox.Ok)
        self.statusbar.clearMessage()

    def evaluate_classifier(self):
        if self.classifier is not None:
            file_test = self.fileBinder.infer('test')
            if file_test:
                self.currentTestData = self.data[file_test]
                index = list(self.currentData.columns).copy()
                has_answer = self.currentDataBinder.infer('c') in self.currentTestData.columns
                index.remove(self.currentDataBinder.infer('c'))
                for k in index:
                    if k not in self.currentTestData.columns:
                        QMessageBox.warning(self, '警告', '测试数据格式不完整！', QMessageBox.Ok)
                        return
                test_data = self.currentTestData[index].to_numpy()
                self.currentTestResult = self.classifier.evaluate(test_data)
                if has_answer:
                    correct: np.ndarray = self.currentTestResult == self.currentTestData[
                        self.currentDataBinder.infer('c')].to_numpy().reshape(-1, 1)
                    self.currentTestAccuracy = correct.sum() / self.currentTestResult.shape[0]
                    QMessageBox.information(self, '提示', '测试成功！正确率%.3f' % self.currentTestAccuracy, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, '提示', '测试成功！', QMessageBox.Ok)
                self.plot_refresh()
            else:
                QMessageBox.warning(self, '警告', '请先指定测试集文件！', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, '警告', '请先创建分类器！', QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
