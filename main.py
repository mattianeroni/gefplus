from PyQt5.QtWidgets import (
    QMainWindow, 
    QApplication,
    QWidget,
    QTabWidget,
    QScrollBar,
    QMenuBar,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QMenu,
    QAction,
    QFileDialog,
    QDialog,
    QMessageBox,
    QLabel,
    QComboBox,
    QPushButton,
    QTableView,
)
from PyQt5.QtCore import QSize, Qt, QMimeData, QAbstractTableModel
from PyQt5.QtGui import QFont, QPalette, QDrag, QPixmap, QColor, QBrush
from PyQt5 import uic 
from pyqtgraph import PlotWidget, plot
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



class DragButton(QPushButton):

    """ An instance of this class represents a droppable button """

    def mouseMoveEvent(self, event):
        """ Implement the movement until the 
        left button is pressed """
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)



class AutoFill (QDialog):

    """ This class represents the UI to auto complete data """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Autofill")
        self.resize(630, 150)
        self.main_window = parent
        self.df = parent.df 
        layout = QGridLayout()
        self.setLayout(layout)

        self.comboboxes = {}
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



class TableModel(QAbstractTableModel):

    """ An instace of this class represents an editable 
    table model used by the table view """

    def __init__(self, df):
        super(TableModel, self).__init__()
        self.df = df

    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self.df.iloc[index.row(), index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # Set the value into the data frame.
            self.df.iloc[index.row(), index.column()] = value
            print(self.df is self.parent.df)
            #print(self.parent.kaplan_meier.df)
            return True
        return False


class TableTab(QWidget):

    """ This widget contains the imported dataset represented 
    as a table """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("table.ui", self)
        self.df = parent.df
        self.model = TableModel(self.df)
        self.table.setModel(self.model)

    def update_df (self, df):
        """ Update the data frame """
        self.df = df 
        self.model.df = df



class KaplanMeierTab(QWidget):

    """ This widget contains functionalities for Kaplan Meier
    curve representation and analysis """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Import graphics
        uic.loadUi("kaplanmeier.ui", self)

        # Save data frame 
        self.df = parent.df 
        self.parent = parent

        # Allow drag n' drop
        self.setAcceptDrops(True)
        self.dropping_widget = None 
        self.dropping_layout = None

        # Init parameters for analysis
        self.survival_var = None 
        self.status_var = None 
        self.filters_var = set()
        
        # Plot characteristics
        self.plotWidget.setBackground('w')
        self.legend = None
        self.lines = []

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

        holder = QWidget()
        holder.setLayout(self.scroll_layout)
        self.scrollArea.setWidget(holder) 

    def dragEnterEvent(self, event):
        """ Method to accept dragging """
        event.accept()

    def add_dummy_widgets(self):
        """ Add a dummy widget to the layouts to ensure 
        the drag n' drop functioning """
        for layout in (self.status_layout, self.survival_layout, self.scroll_layout, self.filters_layout):
            if layout.count() == 0:
                layout.addWidget(QWidget())

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

        
        for layout in (self.filters_layout, self.scroll_layout, self.status_layout, self.survival_layout):
            
            for i in range(layout.count()):  
                
                widget = layout.itemAt(i).widget()
                if widget.x() < pos.x() < widget.x() + widget.size().width() \
                    and widget.y() < pos.y() < widget.y() + widget.size().height():

                    if layout == self.filters_layout:
                        if not isinstance(widget, DragButton):
                            layout.removeWidget(widget)

                        layout.insertWidget(i - 1, button)
                        self.filters_var.add(text)

                    elif layout == self.scroll_layout:
                        if not isinstance(widget, DragButton):
                            layout.removeWidget(widget)
                        
                        layout.insertWidget(i - 1, button)

                    elif layout == self.status_layout:
                        layout.removeWidget(widget) 
                        self.status_var = text 
                        layout.addWidget(button)
                        if isinstance(widget, DragButton):
                            self.scroll_layout.addWidget(widget)  

                    elif layout == self.survival_layout:
                        layout.removeWidget(widget) 
                        self.survival_var = text 
                        layout.addWidget(button)
                        if isinstance(widget, DragButton):
                            self.scroll_layout.addWidget(widget)    

                    event.accept()
                    self.add_dummy_widgets()
                    self.plot()
                    return
        event.ignore()       
        
    def plot(self):
        """ Method to update the plot of the Kaplan Meier curve """
        df = self.df 
        # Reset plot
        if self.legend:
            self.legend.clear()
        for line in self.lines:
            line.clear()
        # New plot
        try:
            if len(self.filters_var) == 0:
                status_series, survival_series = self.df[self.status_var], self.df[self.survival_var]
                time, survival_prob = kaplan_meier_estimator(status_series, survival_series)
                self.line_plot(time, survival_prob)
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
                    self.line_plot(time, survival_prob, label=str(val_combo))
        except Exception as ex:
            self.parent.status_message(str(ex), timeout=5)
    
    def line_plot(self, time, survival, label=None):
        """ Method to generate the plot of a single line """
        # Set plot style
        styles = {'color':'black', 'font-size':'17px'}
        self.plotWidget.setLabel('left', 'Survival', **styles)
        self.plotWidget.setLabel('bottom', 'Time', **styles)
        self.plotWidget.showGrid(x=False, y=True)
        self.legend = self.plotWidget.addLegend()

        # Define colors
        color = np.random.randint(0,255,size=3)
        brush_color = QColor()
        brush_color.setRgb(color[0], color[1], color[2])
        brush = QBrush()
        brush.setColor(brush_color)
        brush.setStyle(Qt.SolidPattern)

        # Plot
        line = self.plotWidget.plot(time, survival, name=label,
            pen=pg.mkPen(color=color,width=3, style=Qt.SolidLine), 
            symbol="o",
            symbolSize=4,
            symbolBrush=brush,
        )
        self.lines.append(line)
        


class MainUI (QMainWindow):

    """ This class represents the main UI the whole application starts from """

    def __init__(self):
        super().__init__()

        # Load graphics and init main window
        uic.loadUi("main.ui", self)

        # Init the app dataframe 
        example_data = {f"Column_{i}" : [f"cell({j},{i})" for j in range(1000)] for i in range(1000)}
        self.df = pd.DataFrame.from_dict(example_data)

        # Init tabs widget
        self.tabs = QTabWidget(self)
        self.centralwidget.layout().addWidget(self.tabs)

        # Init a tab for each supported functionality
        self.table = TableTab(self)
        self.kaplan_meier = KaplanMeierTab(self)

        # Add tabs to the QTabWidget
        self.tabs.addTab(self.table, "Table")
        self.tabs.addTab(self.kaplan_meier, "KaplanMeier")
        
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

    def load_data (self):
        """ Import the dataset """
        self.status_message("Loading...")

        # Import the dataframe
        filename = QFileDialog.getOpenFileName(self, 'Import File', os.getenv('HOME'), 
            "CSV Files (*.csv);;Text Files (*.txt)")
        self.df = pd.read_csv(filename[0], index_col=False)

        # Update widgets dataframe and aspect
        self.table.update_df(self.df)
        self.kaplan_meier.update_df(self.df)

        self.status_message("")


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
