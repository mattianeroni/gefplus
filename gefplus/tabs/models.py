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
from gefplus.components.plotmanager import PlotManager
from gefplus.components.dragmanager import DragManager



class ModelsTab (QWidget):
    
    """ This widget contains functionalities for analysis 
    with multi variate survival models """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("./gefplus/ui/models.ui", self)
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
            multi_choice_layouts=None, 
            parent=self, 
            drop_action=self.train,
        )
        
        self.categorical_df = None 
        example_data = {f"Column_{i}" : np.zeros(100).tolist() for i in range(100)}
        self.test_df = pd.DataFrame.from_dict(example_data)
        self.table_model = TableModel(self.test_df)
        self.test_table.setModel(self.table_model)

        self.estimator = None
        self.one_hot_encoder = None
        self.models = {
            "Cox": CoxPHSurvivalAnalysis
        }

        # Actions
        self.model_box.currentTextChanged.connect(self.train)
        self.test_box.valueChanged.connect(self.train)
        self.import_button.clicked.connect(self.read_test_data)
        self.import_button.clicked.connect(self.prediction)
        self.pred_len_box.valueChanged.connect(self.prediction)

    def reset_stats(self):
        """ Reset training statistics """
        for i in range(self.name_layout.count()):
            self.name_layout.itemAt(i).widget().deleteLater()
        for i in range(self.value_layout.count()):
            self.value_layout.itemAt(i).widget().deleteLater()

    def update_df(self, df):
        """ Set a new data frame """
        self.df = df
        self.drag_manager.populate_buttons(self.df.columns, clear=True)   
        self.plot_manager.reset_plot()
        self.estimator = None 
        self.one_hot_encoder = None 

    @staticmethod
    def build_categorical_df (df, survival, status):
        """ Transform the categorical variables into numeric ones """
        if status is not None and survival is not None:
            df = df.copy()
            df = df.drop([survival, status], axis=1, errors='ignore')
            for header in df.columns:
                if not is_numeric_dtype(df[header]):
                    df[header] = df[header].astype("category")
            one_hot_encoder = OneHotEncoder(allow_drop=False)
            categorical_df = one_hot_encoder.fit_transform(df)
            return one_hot_encoder, categorical_df
        return None, None

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
    
    def train (self):
        """ Run the estimation model """
        EstimatorClass = self.models[self.model_box.currentText()]
        test_size = float(self.test_box.value()) / 100.0
        #try:
        status = self.drag_manager.get_content(self.status_layout)
        survival = self.drag_manager.get_content(self.survival_layout)
        if status is not None and survival is not None:
            y = np.array([ (status, surv)
                for status, surv in zip(self.df[status].values, self.df[survival].values)], 
                dtype=[(status, '?'), (survival, '<f8')]) 
            
            self.one_hot_encoder, self.categorical_df = self.build_categorical_df(self.df, survival, status)
            X_train, X_test, y_train, y_test = train_test_split(self.categorical_df.index, y, test_size=test_size)
            train_df, test_df = self.categorical_df.iloc[X_train], self.categorical_df.iloc[X_test]
            
            features_impact = self.variables_score(
                estimator=EstimatorClass(),
                train_df=train_df,
                y_train=y_train
            )
            
            self.estimator = EstimatorClass()
            self.estimator.fit(train_df, y_train)
            train_score = self.estimator.score(train_df, y_train)
            test_score = self.estimator.score(test_df, y_test)

            self.reset_stats()
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

        #except Exception as ex:
        #    self.parent.status_message(str(ex), timeout=1000)


    def read_test_data (self):
        """ Read a test dataset where to test the trained model """
        try:
            status = self.drag_manager.get_content(self.status_layout)
            survival = self.drag_manager.get_content(self.survival_layout)
            if survival is not None and status is not None:
                filename = QFileDialog.getOpenFileName(self, 'Import Test Dataset', os.getenv('HOME'), 
                        "CSV Files (*.csv);;Text Files (*.txt)")
                self.test_df = pd.read_csv(filename[0], index_col=False)
                self.test_df = self.test_df.drop([survival, status], axis=1, errors='ignore')
                for header in self.test_df.columns:
                    if not is_numeric_dtype(self.test_df[header]):
                        self.test_df[header] = self.test_df[header].astype("category")
                self.table_model = TableModel(self.test_df)
                self.test_table.setModel(self.table_model)

        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)
        

    def prediction (self):
        """ Make a prediction on test dataset """
        try:
            if self.one_hot_encoder is not None and self.estimator is not None:
                test_df = self.one_hot_encoder.transform(self.test_df)
                prediction_length = int(self.pred_len_box.value())
                pred_surv = self.estimator.predict_survival_function(test_df)
                time_points = np.arange(1, prediction_length)
                self.plot_manager.reset_plot()
                for i, surv_func in enumerate(pred_surv):
                    self.plot_manager.line_plot(time_points, surv_func(time_points), label=f"Sample {i + 1}")

        except Exception as ex:
            self.parent.status_message(str(ex), timeout=1000)

