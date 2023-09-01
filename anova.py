from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic 

import numpy as np 
import pandas as pd 
import pingouin as pg 

from dragbutton import DragButton


class AnovaTab(QWidget):

    """ This widget contains functionalities for ANOVA analysis """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Import graphics
        uic.loadUi("./ui/anova.ui", self)

        # Save data frame 
        self.df = parent.df 
        self.parent = parent

        # Allow drag n' drop
        self.setAcceptDrops(True)

        # Init parameters for analysis
        self.scroll_layout = None 
        self.scroll_holder = None
        self.variable = None  
        self.factors = set()

        # Actions of parameters change 
        self.effect_size.currentTextChanged.connect(self.plot_table)
        self.ss_box.valueChanged.connect(self.plot_table)
        self.detail_box.stateChanged.connect(self.plot_table)

    def update_df(self, df):
        """ Set a new data frame """
        self.df = df
        self.populate_buttons()

    def populate_buttons(self):
        """ Method to populate the scrollable are with 
        a draggable button for each field of the dataset """
        df = self.df
        self.scroll_layout = QVBoxLayout()
        for i, header in enumerate(df.columns):
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
        if self.factors_layout.count() == 0:
            self.factors_layout.addWidget(QWidget())
        if self.variable_layout.count() == 0:
            self.variable_layout.addWidget(QWidget())

    def dropEvent(self, event):
        """ Method to accept dropping """
        pos = event.pos()
        button = event.source()
        text = button.text()

        # Reset the variable if the variable button is moved
        if text == self.variable:
            self.variable = None

        # Factor variable is being moved 
        self.factors.discard(text)

        # Verify first a reinsertion in the scroll area
        widget = self.scroll_holder
        if widget.x() < pos.x() < widget.x() + widget.size().width() \
            and widget.y() < pos.y() < widget.y() + widget.size().height():
                self.scroll_layout.addWidget(button)
                event.accept()
                self.add_dummy_widgets()
                self.plot_table()
                return
        
        # Verify the insertion of a variable 
        layout = self.variable_layout
        for i in range(layout.count()):  
            widget = layout.itemAt(i).widget()
            if widget.x() < pos.x() < widget.x() + widget.size().width() \
                and widget.y() < pos.y() < widget.y() + widget.size().height():
                layout.removeWidget(widget) 
                #widget.deleteLater()
                self.variable = text 
                layout.addWidget(button)
                if isinstance(widget, DragButton):
                    self.scroll_layout.addWidget(widget)  
                else:
                    widget.deleteLater()
                event.accept()
                self.add_dummy_widgets()
                self.plot_table()
                return
        
        # Verify the insertion of a new factor
        layout = self.factors_layout
        for i in range(layout.count()):  
            widget = layout.itemAt(i).widget()
            if widget.x() < pos.x() < widget.x() + widget.size().width() \
                and widget.y() < pos.y() < widget.y() + widget.size().height():
                if not isinstance(widget, DragButton):
                    layout.removeWidget(widget) 
                    widget.deleteLater()
                self.factors.add(text) 
                layout.addWidget(button)
                event.accept()
                self.add_dummy_widgets()
                self.plot_table()
                return

        event.ignore()
        
    def plot_table(self):
        """ Method to update the anova results table """
        try:
            # Make anova analysis 
            detailed = self.detail_box.isChecked()
            effsize = self.effect_size.currentText()
            ss_type = self.ss_box.value()
            anova_df = pg.anova(dv=self.variable, between=list(self.factors), data=self.df,
                detailed=detailed, effsize=effsize, ss_type=ss_type)
            
            # Populate the table
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
