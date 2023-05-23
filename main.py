import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
from sksurv.nonparametric import kaplan_meier_estimator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import PySimpleGUI as sg
#sg.theme("DarkBlue3")
#sg.set_options(font=("Courier New", 16))


kaplan_meier_layout = [
    [sg.Canvas(key='-CURVE-')],
    [sg.Text("Survival days: "), sg.Combo([], size=(20,4), enable_events=False, key='-CURVE_X-')],
]



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
                sg.Tab("Anova", [], key='-ANOVA-'),
                sg.Tab("KaplanMeier",kaplan_meier_layout)
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
    return sg.Window("DataTable", table_layout)



def draw_figure(canvas, figure):
    """ Draw figure into Canvas """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# Create the main window
window = sg.Window("GEF+", layout)

# Initialise the data table window
table_window = None

# Initialise the current data dataframe
df = None


# Create an event loop
while True:
    if table_window is not None:
        table_window.read()
    event, values = window.read()

    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    # A file to analyse has been choosen
    if event == "-BROWSER-":
        filename = values["-BROWSER-"]

        # Update the dataframe and the table window
        df = pd.read_csv(filename)
        table_window = get_table_window(df)
        
        # Update fields used for graphs computation
        options = df.columns.values.tolist()
        window["-CURVE_X-"].update(value=options[0], values=options)

        # Compute the Kaplan Meier curve
        time, survival_prob = kaplan_meier_estimator(df["DeathRegistered"], df["SurvivalDays"])
        fig, ax = plt.subplots()
        ax.step(time, survival_prob, where="post")
        ax.set_ylabel("Probability of survival")
        draw_figure(window['-CURVE-'].TKCanvas, fig)



window.close()