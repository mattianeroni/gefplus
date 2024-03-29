from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic, QtGui

import sys 
import os 
import screeninfo

import numpy as np 
import pandas as pd 

from gefplus.autofill import AutoFill
from gefplus.absolute_path import absolute_path
from gefplus.tabs.kaplanmeier import KaplanMeierTab
from gefplus.tabs.table import TableTab
from gefplus.tabs.anova import AnovaTab
from gefplus.tabs.models import ModelsTab
from gefplus.ui.main_ui import Ui_GEF


# Automated scaling on extended screen
#QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
# Handle high resolution displays:

if len(screeninfo.get_monitors()) > 1:
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

#os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"



class MainUI (QMainWindow, Ui_GEF):

    """ This class represents the main UI the whole application starts from """

    def __init__(self):
        super().__init__()

        # Load graphics and init main window
        #uic.loadUi(os.path.abspath("./gefplus/ui/main.ui"), self)
        self.setupUi(self)

        # Icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(absolute_path("static/logosmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(absolute_path("static/export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuExport.setIcon(icon1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(absolute_path("static/import.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImport.setIcon(icon2)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(absolute_path("static/settings.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon3)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(absolute_path("static/autofill.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAutocomplete.setIcon(icon4)

        # Init the app dataframe 
        example_data = {f"Column_{i}" : np.zeros(1000).tolist() for i in range(1000)}
        self.df = pd.DataFrame.from_dict(example_data)

        # Init tabs widget
        self.tabs = QTabWidget(self)
        self.centralwidget.layout().addWidget(self.tabs)

        # Init a tab for each supported functionality
        self.table = TableTab(self)
        self.kaplan_meier = KaplanMeierTab(self)
        self.anova = AnovaTab(self)
        self.models = ModelsTab(self)

        # Add tabs to the QTabWidget
        self.tabs.addTab(self.table, "Table")
        self.tabs.addTab(self.kaplan_meier, "KaplanMeier")
        self.tabs.addTab(self.anova, "Anova")
        self.tabs.addTab(self.models, "Prediction Models")
        
        # Actions
        self.actionImport.triggered.connect(self.load_data)             # import a new dataset
        self.actionAutocomplete.triggered.connect(self.autofill_form)   # autofill data

        # Show window
        self.show()
    
    def box_message (self, message, title="Error", icon=QMessageBox.Critical):
        """ Method to generate a message window """
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def status_message (self, message, timeout=0):
        """ Method to log a message presented in the status bar """
        self.statusbar.showMessage(message, msecs=timeout)

    def update_df (self):
        """ Update the df for all the components """
        self.table.update_df(self.df)
        self.kaplan_meier.update_df(self.df)
        self.anova.update_df(self.df)
        self.models.update_df(self.df)

    def load_data (self):
        """ Import the dataset """
        try:
            self.status_message("Loading...")
            filename = QFileDialog.getOpenFileName(self, 'Import File', os.getenv('HOME'), 
                "CSV Files (*.csv);;Text Files (*.txt)")
            self.df = pd.read_csv(filename[0], index_col=False)
            self.update_df()
            self.status_message("")
            
        except Exception as ex:
            self.status_message(str(ex), timeout=1000)

    def autofill_form (self):
        """ Open UI for data autofilling """
        # Not imported dataframe
        if self.df is None:
            self.box_message("Please, import data before autofilling.")
            return
        # No NaN values to replace
        any_nan = self.df.isnull().values.any()
        if not any_nan:
            self.box_message(
                message="No empty fields detected.",
                title="Warning", 
                icon=QMessageBox.Warning
            )
            return
        
        # Otherwise autocomplete form is open
        autofill_ui = AutoFill(self)
        autofill_ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = MainUI()
    app.exec_()
