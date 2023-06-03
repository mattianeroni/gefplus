import PySimpleGUI as sg
import pandas as pd 
from pandas.api.types import is_numeric_dtype


def import_data_table (filename):
    """ Import a datatable and convert it into a pandas DataFrame """
    # Read the dataframe
    df = pd.read_csv(filename)

    # Convert non-numeric columns to category dtype
    for i in df.columns.values:
        if not is_numeric_dtype(df[i]):
            print(i)
            df[i] = df[i].astype("category")

    return df 



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