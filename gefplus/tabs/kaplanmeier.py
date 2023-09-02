from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5 import uic
import pyqtgraph as pg

import sys 
import os 
import itertools
import functools
import operator

import pandas as pd 
import numpy as np 
from pandas.api.types import is_numeric_dtype
from sksurv.nonparametric import kaplan_meier_estimator

from gefplus.components.dragbutton import DragButton
from gefplus.components.plotmanager import PlotManager



class KaplanMeierTab(QWidget):

    """ This widget contains functionalities for Kaplan Meier
    curve representation and analysis """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi("./gefplus/ui/kaplanmeier.ui", self)
        
        self.df = parent.df 
        self.parent = parent
        self.plot_manager = PlotManager(self.plotWidget)

        # Allow drag n' drop
        self.setAcceptDrops(True)

        # Init parameters for analysis
        self.scroll_layout = None 
        self.scroll_holder = None
        self.survival_var = None 
        self.status_var = None 
        self.filters_var = set()
        

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
        for layout in (self.status_layout, self.survival_layout, self.filters_layout):
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

        # Filter variable is being removed 
        self.filters_var.discard(text)

        # Verify first a reinsertion in the scroll area
        widget = self.scroll_holder
        if widget.x() < pos.x() < widget.x() + widget.size().width() \
            and widget.y() < pos.y() < widget.y() + widget.size().height():
                self.scroll_layout.addWidget(button)
                event.accept()
                self.add_dummy_widgets()
                self.run()
                return
        
        # Then verify the insertion in the other areas --i.e., filters, status, and survival
        for layout in (self.filters_layout, self.status_layout, self.survival_layout):
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget.x() < pos.x() < widget.x() + widget.size().width() \
                    and widget.y() < pos.y() < widget.y() + widget.size().height():

                    if layout == self.filters_layout:
                        if not isinstance(widget, DragButton):
                            layout.removeWidget(widget)
                            widget.deleteLater()
                        layout.insertWidget(i - 1, button)
                        self.filters_var.add(text)

                    elif layout == self.status_layout:
                        layout.removeWidget(widget) 
                        #widget.deleteLater()
                        self.status_var = text 
                        layout.addWidget(button)
                        if isinstance(widget, DragButton):
                            self.scroll_layout.addWidget(widget)  
                        else:
                            widget.deleteLater()

                    elif layout == self.survival_layout:
                        layout.removeWidget(widget) 
                        #widget.deleteLater()
                        self.survival_var = text 
                        layout.addWidget(button)
                        if isinstance(widget, DragButton):
                            self.scroll_layout.addWidget(widget)  
                        else:
                            widget.deleteLater()  

                    event.accept()
                    self.add_dummy_widgets()
                    self.run()
                    return
        event.ignore()       
        
    def run (self):
        """ Method to update the plot of the Kaplan Meier curve """
        df = self.df 
        self.plot_manager.reset_plot()
        try:
            if len(self.filters_var) == 0:
                status_series, survival_series = self.df[self.status_var], self.df[self.survival_var]
                time, survival_prob = kaplan_meier_estimator(status_series, survival_series)
                self.plot_manager.line_plot(time, survival_prob)
            else:
                # Find all combinations of filtered variables
                groups = tuple(df[i].unique() for i in self.filters_var)
                for val_combo in itertools.product(*groups):
                    # Data frame filter function
                    func = functools.reduce(operator.and_, (df[var].eq(value) 
                        for var, value in zip(self.filters_var, val_combo)))
                    # Sub data frame
                    sub_df = df[func]
                    # Compute the curve 
                    time, survival_prob = kaplan_meier_estimator(sub_df[self.status_var], sub_df[self.survival_var])
                    self.plot_manager.line_plot(time, survival_prob, label=str(val_combo))
        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)
    
    
        
