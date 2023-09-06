from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic 

import numpy as np 
import pandas as pd 
import pingouin as pg 

from gefplus.components.dragbutton import DragButton
from gefplus.components.dragmanager import DragManager
from gefplus.ui.main_ui import Ui_anovaTab


class AnovaTab(QWidget, Ui_anovaTab):

    """ This widget contains functionalities for ANOVA analysis """

    def __init__(self, parent=None):
        super().__init__(parent)
        #uic.loadUi("./gefplus/ui/anova.ui", self)
        self.setupUi(self)
        self.df = parent.df 
        self.parent = parent
        self.scroll_layout = QVBoxLayout()
        self.scroll_holder = QWidget()
        self.scroll_holder.setLayout(self.scroll_layout)
        self.scrollArea.setWidget(self.scroll_holder) 
        self.drag_manager = DragManager(
            home_layout=self.scroll_layout, 
            home_widget=self.scroll_holder,
            home_area=self.scrollArea,
            single_choice_layouts=(self.variable_layout, ), 
            multi_choice_layouts=(self.factors_layout, ), 
            parent=self, 
            drop_action=self.plot_table,
        )
        # Actions of parameters change 
        self.effect_size.currentTextChanged.connect(self.plot_table)
        self.ss_box.valueChanged.connect(self.plot_table)
        self.detail_box.stateChanged.connect(self.plot_table)

    def update_df(self, df):
        """ Set a new data frame """
        self.df = df
        self.drag_manager.populate_buttons(self.df.columns, clear=True)
        self.reset_table()
        
    def plot_table(self):
        """ Method to update the anova results table """
        try:
            if self.variable_layout.count() > 0 and self.factors_layout.count() > 0:
                variable = self.drag_manager.get_content(self.variable_layout)
                factors = self.drag_manager.get_content(self.factors_layout)
                if isinstance(factors, tuple):
                    factors = list(factors)
                detailed = self.detail_box.isChecked()
                effsize = self.effect_size.currentText()
                ss_type = self.ss_box.value()
                anova_df = pg.anova(dv=variable, between=factors, data=self.df,
                    detailed=detailed, effsize=effsize, ss_type=ss_type)
                    
                self.table_widget.setColumnCount(anova_df.shape[1])
                self.table_widget.setRowCount(anova_df.shape[0])  
                self.table_widget.setHorizontalHeaderLabels(anova_df.columns)
                for i in range(self.table_widget.rowCount()):
                    for j in range(self.table_widget.columnCount()):
                        self.table_widget.setItem(i, j, QTableWidgetItem(str(anova_df.iloc[i, j])))

        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)
            self.reset_table()

    def reset_table(self):
        """ Reset the anova table """
        self.table_widget.setColumnCount(10)
        self.table_widget.setRowCount(10)  
        for i in range(self.table_widget.rowCount()):
            for j in range(self.table_widget.columnCount()):
                self.table_widget.setItem(i, j, QTableWidgetItem(""))
