import os
import pandas as pd 
import numpy as np
import PySimpleGUI as sg
#sg.theme("DarkBlue3")
#sg.set_options(font=("Courier New", 16))

from components.kaplan_meier import KaplanMeier 
from components.anova import Anova 
from components.table import DataTable, import_data_table
from components.prediction import Prediction
from components.features_selector import FeatureSelector



# Main page layout
layout = [
    [
        sg.Column([[sg.Text("Welcome to GEF+!")]]),
        sg.VSeparator(),
        sg.Column([[
            sg.FileBrowse("Import", file_types=[("CSV", "*.csv"), ("Text", "*.txt")], 
            enable_events=True, key="-BROWSER-")]]),
    ],
    [
        sg.HSeparator()
    ],
    [
        sg.TabGroup(
            [[
                sg.Tab("KaplanMeier", KaplanMeier.layout, key=KaplanMeier.code),
                sg.Tab("Anova", Anova.layout, key=Anova.code),
                sg.Tab("Features", FeatureSelector.layout, key=FeatureSelector.code),
                sg.Tab("Prediction", Prediction.layout, key=Prediction.code),
            ]], 
            key='-TAB_GROUP-'
        ),
    ],
]


# Create the main window
window = sg.Window("GEF+", layout, resizable=True)

# Initialise the data table window
table_window = None

# Initialise the current data dataframe
df = None

# Initialise components
kaplan_maier, anova, features_selector, estimator = None, None, None, None 

# Create an event loop
while True:

    #if table_window is not None:
    #    table_window.read()

    event, values = window.read()

    print(event, values)

    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    # A file to analyse has been choosen
    if event == "-BROWSER-":
        filename = values["-BROWSER-"]

        # Update the dataframe and the table window
        df = import_data_table(filename)
        table_window = DataTable(df, finalize=True) 
        
        # Update components
        kaplan_maier = KaplanMeier(window, df)
        anova = Anova(window, df)
        features_selector = FeatureSelector(window, df)
    
    if kaplan_maier is not None:
        kaplan_maier.trigger(event, values)

    if anova is not None:
        anova.trigger(event, values)

    if features_selector is not None:
        features_selector.trigger(event, values)


window.close()
if table_window is not None:
    table_window.close()