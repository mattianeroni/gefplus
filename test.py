from sksurv.datasets import load_veterans_lung_cancer, load_flchain
from sklearn import set_config
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

import pandas as pd 
from pandas.api.types import is_numeric_dtype

import numpy as np 
import pingouin as pg

from components.table import import_data_table

"""
x, y = load_flchain()
print(x, y)
x["Survival"] = [i[1] for i in y] 
x["Status"] = [i[0] for i in y] 
x.to_csv("incomplete_dataset.csv")
"""

#data_x, data_y = load_flchain()
#print(data_y.columns)
df = import_data_table("incomplete_dataset.csv", True)

print(df["chapter"].dtype)

#df = OneHotEncoder().fit_transform(df)
print(df)

x = tuple(zip(df["SurvivalDays"], df["Status"]))
#print(data_y, type(data_y), data_y.dtype)
#data_x_numeric = OneHotEncoder().fit_transform(data_x)





