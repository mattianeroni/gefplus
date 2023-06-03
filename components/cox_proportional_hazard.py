import PySimpleGUI as sg
from sklearn import set_config
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.preprocessing import OneHotEncoder



class CoxProportionalHazard:

    """ Cox’s proportional hazard’s is a linear model 
    to estimate the impact each variable has on survival """

    code = "-COX_PH-"

    layout = [

    ]


    def __init__ (self, window, df):
        """ 
        Initialise the component.

        :param window: The window where the component is drawn
        :param df: The dataframe of the main data table 
        
        NOTE: The dataframe kept in memory by the Cox Proportional Hazard's model
        may differ from original data table, because cathegorical variables are 
        made numeric.

        """
        self.window = window 
        self.df = OneHotEncoder().fit_transform(df)