from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic 

import sys 
import os 

import numpy as np 
import pandas as pd 

from autofill import AutoFill
from gefplus.tabs.kaplanmeier import KaplanMeierTab
from gefplus.tabs.table import TableTab
from gefplus.tabs.anova import AnovaTab
from gefplus.tabs.models import ModelsTab

# Automated scaling on extended screen
#QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
# Handle high resolution displays:
#if hasattr(Qt, 'AA_EnableHighDpiScaling'):
#    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainUI (QMainWindow):

    """ This class represents the main UI the whole application starts from """

    def __init__(self):
        super().__init__()

        # Load graphics and init main window
        uic.loadUi("./gefplus/ui/main.ui", self)

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
