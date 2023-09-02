from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5 import uic 
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import os
import pandas as pd 
import numpy as np 
from pandas.api.types import is_numeric_dtype

from sksurv.preprocessing import OneHotEncoder
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sklearn.model_selection import train_test_split

from gefplus.components.dragbutton import DragButton
from gefplus.components.tablemodel import TableModel



class ModelsTab (QWidget):
    
    """ This widget contains functionalities for analysis 
    with multi variate survival models """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Import graphics
        uic.loadUi("./gefplus/ui/models.ui", self)
        self.parent = parent

        # Save data frame 
        self.df = parent.df 
        self.categorical_df = None 
        example_data = {f"Column_{i}" : np.zeros(1000).tolist() for i in range(1000)}
        self.test_df = pd.DataFrame.from_dict(example_data)

        # Allow drag n' drop
        self.setAcceptDrops(True)

        # Init parameters for analysis
        self.scroll_layout = None 
        self.scroll_holder = None
        self.survival_var = None 
        self.status_var = None 

        self.model_var = None
        self.estimator = None
        self.one_hot_encoder = None
        self.models = {
            "Cox": CoxPHSurvivalAnalysis
        }

        self.table_model = TableModel(self.test_df)
        self.test_table.setModel(self.table_model)
        
        # Plot characteristics
        self.plotWidget.setBackground('w')
        self.legend = None
        self.lines = []

        # Actions
        self.model_box.currentTextChanged.connect(self.run)
        self.test_box.valueChanged.connect(self.run)
        self.pred_len_box.valueChanged.connect(self.prediction)
        self.import_button.clicked.connect(self.read_test_data)

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
                self.run()
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


    def build_categorical_df (self):
        """ Transform the categorical variables into numeric ones """
        if self.status_var is not None and self.survival_var is not None:
            df = self.df.copy()
            df = df.drop([self.survival_var, self.status_var], axis=1, errors='ignore')
            for header in df.columns:
                if not is_numeric_dtype(df[header]):
                    df[header] = df[header].astype("category")
            self.one_hot_encoder = OneHotEncoder(allow_drop=False)
            self.categorical_df = self.one_hot_encoder.fit_transform(df)

    @staticmethod
    def variables_score (estimator, train_df, y_train):
        """ Assign a score to each feature according to its 
        impact on the prediction """
        n_features = train_df.shape[1]
        scores = np.empty(n_features)
        for j in range(n_features):
            Xj = train_df.values[:, j : j + 1]
            estimator.fit(Xj, y_train)
            scores[j] = estimator.score(Xj, y_train)
        return pd.Series(scores, index=train_df.columns)
    
    def run (self):
        """ Run the estimation model """
        self.model_var = self.model_box.currentText()
        EstimatorClass = self.models[self.model_var]
        test_size = float(self.test_box.value()) / 100.0

        try:
            if self.status_var is not None and self.survival_var is not None:
                # Extract output in the correct format for the estimator
                y = np.array([ (status, surv)
                    for status, surv in zip(self.df[self.status_var].values, self.df[self.survival_var].values)], 
                    dtype=[(self.status_var, '?'), (self.survival_var, '<f8')]) 
                
                # Clean categorical data
                self.build_categorical_df()
                df = self.categorical_df
                # Build train and test datasets
                X_train, X_test, y_train, y_test = train_test_split(df.index, y, test_size=test_size)
                train_df, test_df = df.iloc[X_train], df.iloc[X_test]
                # Record the impact of each feature singularly 
                features_impact = self.variables_score(
                    estimator=EstimatorClass(),
                    train_df=train_df,
                    y_train=y_train
                )
                # Train and test the model on the whole dataset 
                self.estimator = EstimatorClass()
                self.estimator.fit(train_df, y_train)
                train_score = self.estimator.score(train_df, y_train)
                test_score = self.estimator.score(test_df, y_test)

                # Write stats
                for i in range(self.name_layout.count()):
                    self.name_layout.itemAt(i).widget().deleteLater()
                for i in range(self.value_layout.count()):
                    self.value_layout.itemAt(i).widget().deleteLater()

                for name, value in features_impact.items():
                    name_label = QLabel(f"{name}: ")
                    value_label = QLabel(f"{round(value, 5)}")
                    name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    value_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    self.name_layout.addWidget(name_label)
                    self.value_layout.addWidget(value_label)
                self.name_layout.addWidget(QLabel("Train score: "))
                self.name_layout.addWidget(QLabel("Test score: "))
                self.value_layout.addWidget(QLabel(f"{round(train_score, 5)}"))
                self.value_layout.addWidget(QLabel(f"{round(test_score, 5)}"))

        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)


    def read_test_data (self):
        """ Read a test dataset where to test the trained model """
        #try:
        filename = QFileDialog.getOpenFileName(self, 'Import Test Dataset', os.getenv('HOME'), 
                "CSV Files (*.csv);;Text Files (*.txt)")
        self.test_df = pd.read_csv(filename[0], index_col=False)
        self.test_df = self.test_df.drop([self.survival_var, self.status_var], axis=1, errors='ignore')
        for header in self.test_df.columns:
            if not is_numeric_dtype(self.test_df[header]):
                self.test_df[header] = self.test_df[header].astype("category")
        self.table_model = TableModel(self.test_df)
        self.test_table.setModel(self.table_model)
        self.prediction()
        #except Exception as ex:
        #    self.parent.status_message(str(ex), timeout=1000)
        

    def prediction (self):
        """ Make a prediction on test dataset """
        try:
            self.build_categorical_df()
            test_df = self.one_hot_encoder.transform(self.test_df)
            prediction_length = int(self.pred_len_box.value())

            # Plot the tests
            if self.legend: self.legend.clear()
            for line in self.lines: line.clear()
            pred_surv = self.estimator.predict_survival_function(test_df)
            time_points = np.arange(1, prediction_length)
            for i, surv_func in enumerate(pred_surv):
                self.line_plot(time_points, surv_func(time_points), label=f"Sample {i + 1}")
        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)


    def line_plot(self, time, survival, *, label=None, width=3, style=Qt.SolidLine, color=None):
        """ Method to generate the plot of a single line """
        # Set plot style
        styles = {'color':'black', 'font-size':'17px'}
        self.plotWidget.setLabel('left', 'Survival', **styles)
        self.plotWidget.setLabel('bottom', 'Time', **styles)
        self.plotWidget.showGrid(x=False, y=True)
        self.legend = self.plotWidget.addLegend()

        # Define colors
        if color is None:
            color = np.random.randint(0, 255, size=3)
        brush_color = QColor()
        brush_color.setRgb(color[0], color[1], color[2])
        brush = QBrush()
        brush.setColor(brush_color)
        brush.setStyle(Qt.SolidPattern)

        # Plot
        line = self.plotWidget.plot(time, survival, name=label,
            pen=pg.mkPen(color=color, width=width, style=style), 
            symbol="o",
            symbolSize=4,
            symbolBrush=brush,
        )
        self.lines.append(line)

