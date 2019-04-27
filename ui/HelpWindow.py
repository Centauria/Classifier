# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HelpWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HelpWindow(object):
    def setupUi(self, HelpWindow):
        HelpWindow.setObjectName("HelpWindow")
        HelpWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(HelpWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 800, 550))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab)
        self.textBrowser.setGeometry(QtCore.QRect(40, 40, 256, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        HelpWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(HelpWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        HelpWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(HelpWindow)
        self.statusbar.setObjectName("statusbar")
        HelpWindow.setStatusBar(self.statusbar)

        self.retranslateUi(HelpWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

    def retranslateUi(self, HelpWindow):
        _translate = QtCore.QCoreApplication.translate
        HelpWindow.setWindowTitle(_translate("HelpWindow", "分类器 帮助"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("HelpWindow", "感知机"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("HelpWindow", "Tab 2"))

