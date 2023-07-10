import PySimpleGUI as sg
import pandas as pd
from pandas.api.types import is_numeric_dtype 
import numpy as np 
import matplotlib.pyplot as plt 
import sklearn
from sksurv.preprocessing import OneHotEncoder
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.metrics import (
    concordance_index_censored,
    concordance_index_ipcw,
    cumulative_dynamic_auc,
    integrated_brier_score,
)

sklearn.set_config(display="text")
plt.rcParams["figure.figsize"] = [7.2, 4.8]



class FeatureSelector:

    """ Cox’s proportional hazard’s is a linear model 
    to estimate the impact each variable has on survival """

    code = "-FEATURES_SELECTOR-"

    layout = [
        [
            sg.Table(
                values=[], 
                headings=[" " * 5  + "Feature" + " " * 5, " " * 5 + "Score" + " " * 5], 
                auto_size_columns=False, 
                enable_events=True, 
                col_widths=[40, 20],
                justification='center',
                key="-FEATURES_SELECTOR_TABLE-",
            )
        ],
        [
            sg.Canvas(size=(40, 40), key='-AUC_IMAGE-')
        ],
        [   
            sg.Text("Survival:",), sg.Combo([], size=(20,4), enable_events=True, key='-FEATURES_SELECTOR_SURVIVAL-'), 
            sg.Text("Status:"), sg.Combo([], size=(20,4), enable_events=True, key='-FEATURES_SELECTOR_STATUS-'),
            sg.Text("Model:"), sg.Combo([], size=(20,4), enable_events=True, key='-FEATURES_SELECTOR_MODEL-'),
        ],
        [sg.Text("Affected features:")],
        [sg.Text("         "), sg.Listbox([], size=(20, 4), select_mode='extended', enable_events=True,  key='-AFFECTED_FEATURES-')],
        [
            sg.FileSaveAs("Save Scores", enable_events=True, key="-SAVE_FEATURES-", file_types=(('CSV', '*.csv'),)),
            sg.FileSaveAs("Save AUC", enable_events=True, key="-SAVE_AUC-", file_types=(('PNG', '*.png'),)),
        ]
    ]


    def __init__ (self, window, df):
        """ 
        Initialise the component.

        :param window: The window where the component is drawn
        :param df: The dataframe of the main data table 
        
        NOTE: The dataframe kept in memory may differ from original data 
        table, because cathegorical variables are made numeric.

        """
        self.window = window 
        self.df = OneHotEncoder().fit_transform(df)
        
        # Fixed attributes
        #self.headers = (" " * 5  + "Feature" + " " * 5, " " * 5 + "Score" + " " * 5)
        self.models = {
            "Cox": CoxPHSurvivalAnalysis,
        }
        self.supported_models = tuple(self.models.keys())

        # Define values for combos
        fields = self.df.columns.values.tolist()
        window["-FEATURES_SELECTOR_SURVIVAL-"].update(value=fields[0], values=fields)
        window["-FEATURES_SELECTOR_STATUS-"].update(value=fields[0], values=fields)
        window["-FEATURES_SELECTOR_MODEL-"].update(value=self.supported_models[0], values=self.supported_models)

        # Affected features
        fields = [i for i in df.columns.values if is_numeric_dtype(df[i])]
        window["-ANOVA_FACTORS-"].update(fields)

        # Compute the starting results if possible
        self.results = None


    @staticmethod
    def _feature_score (estimator, feature_x, y):
        estimator.fit(feature_x, y)
        return estimator.score(feature_x, y)


    def trigger(self, event, values):
        if event == '-FEATURES_SELECTOR_SURVIVAL-' or event == '-FEATURES_SELECTOR_STATUS-' or event == '-FEATURES_SELECTOR_MODEL-':
            try:
                # Intantiate the estimator
                estimator = self.models[values["-FEATURES_SELECTOR_MODEL-"]]()

                # Get the expected output
                status_field, survival_field = values["-FEATURES_SELECTOR_STATUS-"], values["-FEATURES_SELECTOR_SURVIVAL-"]
                y = np.array(list(zip(self.df[status_field], self.df[survival_field])), dtype=[('Status', '?'), ('Survival', '<f8')])

                # Compute the scores for each feature
                fields_to_score = tuple(field for field in self.df.columns if field != status_field and field != survival_field)

                scores = np.array([
                    self._feature_score(estimator, self.df[field].values.reshape(-1, 1), y)  for field in fields_to_score
                ]).astype(np.float32)

                self.results = pd.Series(scores, index=fields_to_score).sort_values(ascending=False)
                self.window["-FEATURES_SELECTOR_TABLE-"].update( list(zip(self.results.index.values, self.results.values)) )

            except Exception as ex:
                self.results = None

            
        # Save the anova table
        elif event == "-SAVE_FEATURES-":
            self.results.to_csv(values["-SAVE_FEATURES-"])
        
        # Save the AUC curve of features
        elif event == "-SAVE_AUC-":
            plt.figure(self.figure.number)
            plt.savefig(values["-SAVE_AUC-"])