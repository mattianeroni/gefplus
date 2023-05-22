import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import PySimpleGUI as sg
#sg.theme("DarkBlue3")
#sg.set_options(font=("Courier New", 16))

import layout



def update_preview(window, **table_options):

    if window is not None:
        window.close()

    new_layout = layout.new()
    new_layout[1] = [sg.Table(**table_options, key="-PREVIEW-")]
    return sg.Window("GEF+", new_layout, finalize=True)



# Create the window
window = sg.Window("GEF+", layout.new(), finalize=True)


# Create an event loop
while True:
    event, values = window.read()

    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    # Show files in the selected folder
    elif event == "-BROWSER-":
        filename = values["-BROWSER-"]
        df = pd.read_csv(filename, index_col=0)
        window = update_preview(window, headings=df.columns.values.tolist(), values=df.values.tolist())


window.close()