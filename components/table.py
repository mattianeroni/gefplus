import PySimpleGUI as sg
import pandas as pd 


class DataTable(sg.Window):

    def __init__(self, df, **kwargs):
        self.layout = [
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
        super().__init__("DataTable", self.layout, **kwargs)