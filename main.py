import os
import pandas as pd 
import numpy as np
import PySimpleGUI as sg
#sg.theme("DarkBlue3")
#sg.set_options(font=("Courier New", 16))

from components.kaplan_meier import KaplanMeier 
from components.anova import Anova 



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
            ]], 
            key='-TAB_GROUP-'
        ),
    ],
]




def get_table_window(df):
    """ Create a new window to show the data table """
    table_layout = [
        [
            sg.Table(
                values=df.values.tolist(), 
                headings=df.columns.values.tolist(), 
                auto_size_columns=True, 
                enable_events=True, 
                size=(40, 20),
                justification='center',
            )
        ]
    ]
    return sg.Window("DataTable", table_layout, finalize=True)






# Create the main window
window = sg.Window("GEF+", layout, resizable=True)

# Initialise the data table window
table_window = None

# Initialise the current data dataframe
df = None

# Initialise components
kaplan_maier, anova = None, None 

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
        df = pd.read_csv(filename)
        table_window = get_table_window(df)
        
        # Update components
        kaplan_maier = KaplanMeier(window, df)
        anova = Anova(window, df)
    
    if kaplan_maier is not None:
        kaplan_maier.trigger(event, values)

    if anova is not None:
        anova.trigger(event, values)


window.close()
if table_window is not None:
    table_window.close()