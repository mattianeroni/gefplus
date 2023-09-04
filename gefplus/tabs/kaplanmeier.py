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
from gefplus.components.dragmanager import DragManager



class KaplanMeierTab (QWidget):

    """ This widget contains functionalities for Kaplan Meier
    curve representation and analysis """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("./gefplus/ui/kaplanmeier.ui", self)
        self.df = parent.df 
        self.parent = parent
        self.scroll_layout = QVBoxLayout()
        self.scroll_holder = QWidget()
        self.scroll_holder.setLayout(self.scroll_layout)
        self.scrollArea.setWidget(self.scroll_holder) 
        self.plot_manager = PlotManager(self.plotWidget, parent=self)
        self.drag_manager = DragManager(
            home_layout=self.scroll_layout, 
            home_widget=self.scroll_holder,
            home_area=self.scrollArea,
            single_choice_layouts=(self.survival_layout, self.status_layout), 
            multi_choice_layouts=(self.filters_layout, ), 
            parent=self, 
            drop_action=self.kaplan_meier_plot,
        )

    def update_df(self, df):
        """ Set a new data frame """
        self.df = df
        self.drag_manager.populate_buttons(self.df.columns, clear=True)
        self.plot_manager.reset_plot()
        
    def kaplan_meier_plot (self):
        """ Method to update the plot of the Kaplan Meier curve """
        df = self.df 
        self.plot_manager.reset_plot()
        try:
            if self.status_layout.count() > 0 and self.survival_layout.count() > 0:
                filters = self.drag_manager.get_content(self.filters_layout)
                status = self.drag_manager.get_content(self.status_layout)
                survival = self.drag_manager.get_content(self.survival_layout)

                if len(filters) == 0:
                    status_series, survival_series = self.df[status], self.df[survival]
                    time, survival_prob = kaplan_meier_estimator(status_series, survival_series)
                    self.plot_manager.line_plot(time, survival_prob)
                else:
                    # Find all combinations of filtered variables
                    groups = tuple(df[i].unique() for i in filters)
                    for val_combo in itertools.product(*groups):
                        # Data frame filter function
                        func = functools.reduce(operator.and_, (df[var].eq(value) 
                            for var, value in zip(filters, val_combo)))
                        # Sub data frame
                        sub_df = df[func]
                        # Compute the curve 
                        time, survival_prob = kaplan_meier_estimator(sub_df[status], sub_df[survival])
                        self.plot_manager.line_plot(time, survival_prob, label=str(val_combo))

        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)
    
    
        
