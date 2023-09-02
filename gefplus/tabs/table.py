from PyQt5.QtWidgets import QWidget
from PyQt5 import uic 

from gefplus.components.tablemodel import TableModel


class TableTab(QWidget):

    """ This widget contains the imported dataset represented 
    as a table """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("./gefplus/ui/table.ui", self)
        self.df = parent.df
        self.model = TableModel(self.df)
        self.table.setModel(self.model)

    def update_df (self, df):
        """ Update the data frame """
        self.df = df 
        self.model = TableModel(df)
        self.table.setModel(self.model)