import PySimpleGUI as sg
import pandas as pd 
from pandas.api.types import is_numeric_dtype
from sklearn.impute import SimpleImputer



def import_data_table (filename, autofill=False):
    """ Import a datatable and convert it into a pandas DataFrame """
    # Read the dataframe
    df = pd.read_csv(filename)
    if autofill:
        cols = df.columns
        df = pd.DataFrame(SimpleImputer(strategy="most_frequent").fit(df.values).transform(df.values).tolist())
        df.columns = cols

    # Convert non-numeric columns to category dtype
    for i in df.columns.values:
        if not is_numeric_dtype(df[i]):
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