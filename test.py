import pandas as pd 
from pandas.api.types import is_numeric_dtype

import numpy as np 
import itertools
import functools
import operator
import pyqtgraph as pg 
import pingouin

from sksurv.preprocessing import OneHotEncoder
from sksurv.datasets import load_veterans_lung_cancer

df = pd.read_csv("dataset.csv", index_col=None)

def categorical_df (df):
    """ Transform the categorical variables into numeric ones """
    df = df.copy()
    df = df.drop(["SurvivalDays", "Status"], axis=1)
    for header in df.columns:
        if not is_numeric_dtype(df[header]):
            df[header] = df[header].astype("category")
    return OneHotEncoder().fit_transform(df)

numeric_df = categorical_df(df)
print(numeric_df)



