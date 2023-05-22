import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import PySimpleGUI as sg





browsing_column = [
    [
        sg.Text("File Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")
    ],
]

file_preview_column = [
    [sg.Text("File Preview")],
    #[sg.Text(size=(40, 1), key="-TOUT-")],
    #[sg.Image(key="-IMAGE-")],
    [sg.Table(values=[], headings=[], size=(40,21), auto_size_columns=True, enable_events=True, key="-PREVIEW-")],
]



layout = [
    [
        sg.Column(browsing_column),
        sg.VSeperator(),
        sg.Column(file_preview_column),
    ]
]

# Create the window
window = sg.Window("Surpy", layout)
#sg.theme("DarkBlue3")
#sg.set_options(font=("Courier New", 16))

# Create an event loop
while True:
    event, values = window.read()

    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    # Show files in the selected folder
    elif event == "-FOLDER-":
        folder = values["-FOLDER-"]
        file_list = os.listdir(folder)

        fnames = [
            filename
        for filename in file_list
        if os.path.isfile(os.path.join(folder, filename)) and filename.lower().endswith((".png",".csv", ".txt"))
        ]
        window["-FILE LIST-"].update(fnames)

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
            df = pd.read_csv(filename, index_col=0)
            new_table = sg.Table(values=df.values.tolist(), headings=df.columns.values.tolist(), size=(40,21), auto_size_columns=True, enable_events=True, key="-PREVIEW-")
            #new_table = sg.Table(values=, headings=[], size=(40,21), auto_size_columns=True, enable_events=True, key="-PREVIEW-")
            window["-PREVIEW-"].update(new_table) #values=df.values.tolist(), headings=df.columns.values.tolist())
            #values=df.values.tolist(), heaings=df.columns.values.tolist())
            #åwindow.refresh()
        except:
            pass

    

window.close()