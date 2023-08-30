from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5 import uic 
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import pandas as pd 
import numpy as np 
from pandas.api.types import is_numeric_dtype

from sksurv.preprocessing import OneHotEncoder
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sklearn.model_selection import train_test_split

from dragbutton import DragButton



class ModelsTab (QWidget):
    
    """ This widget contains functionalities for analysis 
    with multi variate survival models """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Import graphics
        uic.loadUi("./ui/models.ui", self)

        # Save data frame 
        self.df = parent.df 
        self.parent = parent

        # Allow drag n' drop
        self.setAcceptDrops(True)

        # Init parameters for analysis
        self.scroll_layout = None 
        self.scroll_holder = None
        self.survival_var = None 
        self.status_var = None 
        self.model_var = None

        self.models = {
            "Cox": CoxPHSurvivalAnalysis
        }
        
        # Plot characteristics
        self.plotWidget.setBackground('w')
        self.legend = None
        self.lines = []

        # Actions
        self.model_box.currentTextChanged.connect(self.predict)
        self.test_box.valueChanged.connect(self.predict)

    def update_df(self, df):
        """ Set a new data frame """
        self.df = df
        self.populate_buttons()

    def populate_buttons(self):
        """ Method to populate the scrollable are with 
        a draggable button for each field of the dataset """
        df = self.df
        self.scroll_layout = QVBoxLayout()
        for header in df.columns:
            btn = DragButton(header, self)
            self.scroll_layout.addWidget(btn)

        self.scroll_holder = QWidget()
        self.scroll_holder.setLayout(self.scroll_layout)
        self.scrollArea.setWidget(self.scroll_holder) 

    def dragEnterEvent(self, event):
        """ Method to accept dragging """
        event.accept()

    def add_dummy_widgets(self):
        """ Add a dummy widget to the layouts to ensure 
        the drag n' drop functioning """
        for layout in (self.status_layout, self.survival_layout):
            if layout.count() == 0:
                widget = QWidget()
                widget.setStyleSheet("margin:5px; border:1px solid rgb(180, 180, 180);")
                widget.setMinimumSize(100, 40)
                widget.setMaximumSize(16777215, 40)
                layout.addWidget(widget)

    def dropEvent(self, event):
        """ Method to accept dropping """
        pos = event.pos()
        button = event.source()
        text = button.text()

        # Status variable button is being moved
        if text == self.status_var:
            self.status_var = None

        # Survival variable is being moved
        if text == self.survival_var:
            self.survival_var = None

        # Verify first a reinsertion in the scroll area
        widget = self.scroll_holder
        if widget.x() < pos.x() < widget.x() + widget.size().width() \
            and widget.y() < pos.y() < widget.y() + widget.size().height():
                self.scroll_layout.addWidget(button)
                event.accept()
                self.add_dummy_widgets()
                self.predict()
                return
        
        # Then verify the insertion in the other areas --i.e., filters, status, and survival
        for layout in (self.status_layout, self.survival_layout):
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget.x() < pos.x() < widget.x() + widget.size().width() \
                    and widget.y() < pos.y() < widget.y() + widget.size().height():

                    if layout == self.status_layout:
                        self.status_var = text 
                    elif layout == self.survival_layout:
                        self.survival_var = text 

                    layout.removeWidget(widget) 
                    widget.deleteLater()
                    layout.addWidget(button)
                    if isinstance(widget, DragButton):
                        self.scroll_layout.addWidget(widget)    

                    event.accept()
                    self.add_dummy_widgets()
                    self.predict()
                    return
        event.ignore()       

    def categorical_df (self):
        """ Transform the categorical variables into numeric ones """
        df = self.df.copy()
        df = df.drop([self.survival_var, self.status_var], axis=1)
        for header in df.columns:
            if not is_numeric_dtype(df[header]):
                df[header] = df[header].astype("category")
        return OneHotEncoder().fit_transform(df)
    
    def predict (self):
        """ Run the estimation model """
        self.model_var = self.model_box.currentText()
        test_size = float(self.test_box.value()) / 100.0

        try:
            y = np.array([ (status, surv)
                for status, surv in zip(self.df[self.status_var].values, self.df[self.survival_var].values)], 
                dtype=[(self.status_var, '?'), (self.survival_var, '<f8')])
            
            df = self.categorical_df()
            df = OneHotEncoder().fit_transform(df)

            X_train, X_test, y_train, y_test = train_test_split(df.index, y, test_size=test_size)
            train_df, test_df = df.iloc[X_train], df.iloc[X_test]
            
            estimator = self.models[self.model_var]()
            estimator.fit(train_df, y_train)

        except Exception as ex:
            print(ex)
            self.parent.status_message(str(ex), timeout=1000)



