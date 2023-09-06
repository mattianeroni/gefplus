# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gefplus/ui/kaplanmeier.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_kaplanmeierTab(object):
    def setupUi(self, kaplanmeierTab):
        kaplanmeierTab.setObjectName("kaplanmeierTab")
        kaplanmeierTab.resize(612, 400)
        kaplanmeierTab.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout = QtWidgets.QHBoxLayout(kaplanmeierTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.labelDays = QtWidgets.QLabel(kaplanmeierTab)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.labelDays.setFont(font)
        self.labelDays.setTextFormat(QtCore.Qt.RichText)
        self.labelDays.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelDays.setObjectName("labelDays")
        self.gridLayout.addWidget(self.labelDays, 1, 0, 1, 1)
        self.labelStatus = QtWidgets.QLabel(kaplanmeierTab)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.labelStatus.setFont(font)
        self.labelStatus.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout.addWidget(self.labelStatus, 2, 0, 1, 1)
        self.status_layout = QtWidgets.QHBoxLayout()
        self.status_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.status_layout.setObjectName("status_layout")
        self.status_widget = QtWidgets.QWidget(kaplanmeierTab)
        self.status_widget.setEnabled(False)
        self.status_widget.setMinimumSize(QtCore.QSize(100, 40))
        self.status_widget.setMaximumSize(QtCore.QSize(16777215, 40))
        self.status_widget.setAutoFillBackground(False)
        self.status_widget.setStyleSheet("margin:5px; border:1px solid rgb(180,180, 180);")
        self.status_widget.setObjectName("status_widget")
        self.status_layout.addWidget(self.status_widget)
        self.gridLayout.addLayout(self.status_layout, 2, 1, 1, 1)
        self.labelFilters = QtWidgets.QLabel(kaplanmeierTab)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.labelFilters.setFont(font)
        self.labelFilters.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelFilters.setObjectName("labelFilters")
        self.gridLayout.addWidget(self.labelFilters, 3, 0, 1, 1)
        self.plotWidget = PlotWidget(kaplanmeierTab)
        self.plotWidget.setAutoFillBackground(False)
        self.plotWidget.setStyleSheet("")
        self.plotWidget.setObjectName("plotWidget")
        self.gridLayout.addWidget(self.plotWidget, 0, 1, 1, 1)
        self.filters_layout = QtWidgets.QHBoxLayout()
        self.filters_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.filters_layout.setObjectName("filters_layout")
        self.filters_widget = QtWidgets.QWidget(kaplanmeierTab)
        self.filters_widget.setEnabled(False)
        self.filters_widget.setMinimumSize(QtCore.QSize(100, 40))
        self.filters_widget.setMaximumSize(QtCore.QSize(16777215, 40))
        self.filters_widget.setAutoFillBackground(False)
        self.filters_widget.setStyleSheet("margin:5px; border:1px solid rgb(180, 180, 180);")
        self.filters_widget.setObjectName("filters_widget")
        self.filters_layout.addWidget(self.filters_widget)
        self.gridLayout.addLayout(self.filters_layout, 3, 1, 1, 1)
        self.survival_layout = QtWidgets.QHBoxLayout()
        self.survival_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.survival_layout.setObjectName("survival_layout")
        self.survival_widget = QtWidgets.QWidget(kaplanmeierTab)
        self.survival_widget.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.survival_widget.sizePolicy().hasHeightForWidth())
        self.survival_widget.setSizePolicy(sizePolicy)
        self.survival_widget.setMinimumSize(QtCore.QSize(100, 40))
        self.survival_widget.setMaximumSize(QtCore.QSize(16777215, 40))
        self.survival_widget.setAutoFillBackground(False)
        self.survival_widget.setStyleSheet("margin:5px; border:1px solid rgb(180, 180, 180);")
        self.survival_widget.setObjectName("survival_widget")
        self.survival_layout.addWidget(self.survival_widget)
        self.gridLayout.addLayout(self.survival_layout, 1, 1, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(kaplanmeierTab)
        self.scrollArea.setEnabled(True)
        self.scrollArea.setMaximumSize(QtCore.QSize(300, 16777215))
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setStyleSheet("")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_widget.setGeometry(QtCore.QRect(0, 0, 278, 137))
        self.scroll_widget.setObjectName("scroll_widget")
        self.scrollArea.setWidget(self.scroll_widget)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(kaplanmeierTab)
        QtCore.QMetaObject.connectSlotsByName(kaplanmeierTab)

    def retranslateUi(self, kaplanmeierTab):
        _translate = QtCore.QCoreApplication.translate
        kaplanmeierTab.setWindowTitle(_translate("kaplanmeierTab", "Form"))
        self.labelDays.setText(_translate("kaplanmeierTab", "Survival Days: "))
        self.labelStatus.setText(_translate("kaplanmeierTab", "Status: "))
        self.labelFilters.setText(_translate("kaplanmeierTab", "Filters: "))
from pyqtgraph import PlotWidget