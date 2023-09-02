from PyQt5.QtWidgets import (    
    QMessageBox,
    QLabel,
    QComboBox,
    QDialog,
    QPushButton,
    QGridLayout,
)

import pandas as pd 
import numpy as np 
from pandas.api.types import is_numeric_dtype



class AutoFill (QDialog):

    """ This class represents the UI to auto complete data """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Autofill")
        self.resize(630, 150)
        self.main_window = parent
        self.df = parent.df 
        self.comboboxes = {}
        layout = QGridLayout()
        self.setLayout(layout)
        df = self.df

        for i, field in enumerate(df.columns.values):
            # Labels
            label = QLabel(field + ": ")
            label.setStyleSheet("font-weight: bold")
            layout.addWidget(label, i, 0)
            
            # Dropdown menus
            combobox = QComboBox()
            options = ('Max', 'Mean') if is_numeric_dtype(df[field]) else ("Most Frequent", "Skewed")
            combobox.addItems(options)
            layout.addWidget(combobox, i, 1)
            self.comboboxes[field] = combobox

        ok_button = QPushButton("Ok")
        layout.addWidget(ok_button, len(df.columns), 1)
        ok_button.clicked.connect(self.autofill)
    
    def autofill (self):
        """ Method to autocatically fill missing cells in dataset """
        df = self.df 
        try:
            for field, combobox in self.comboboxes.items():
                filltype = str(combobox.currentText())

                if filltype == "Max":
                    series = df[field]
                    df[field].fillna(series[~series.isna()].max(), inplace=True)

                elif filltype == "Mean":
                    series = df[field]
                    df[field].fillna(series[~series.isna()].mean(), inplace=True)

                elif filltype == "Most Frequent":
                    value = df[field].value_counts().idxmax()
                    df[field].fillna(value, inplace=True)

                elif filltype == "Skewed":
                    # Compute probabilities associated to non NaN values
                    not_null_series = df[~df[field].isna()][field]
                    counts_df = not_null_series.value_counts()
                    probs = counts_df.values / counts_df.values.sum() 

                    # Compute new values 
                    nan_idx = df[field].isna()
                    new_vals = np.random.choice(counts_df.index, size=len(nan_idx[nan_idx == True]), p=probs)

                    # Assign new values to original dataframe
                    series = df[field].copy() 
                    series[series.isna()] = new_vals
                    df[field] = series
        except:
            self.main_window.box_message("404. Unknown error.")

        self.main_window.populate_table()
        self.close()