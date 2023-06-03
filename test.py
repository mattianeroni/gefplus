from sksurv.datasets import load_veterans_lung_cancer
from sklearn import set_config
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.preprocessing import OneHotEncoder


import pandas as pd 
from pandas.api.types import is_numeric_dtype

import numpy as np 
import pingouin as pg

from components.table import import_data_table

data_x, data_y = load_veterans_lung_cancer()

df = import_data_table("results.csv")


#print( df.dtypes )

data_x_numeric = OneHotEncoder().fit_transform(data_x)

set_config(display="text")  # displays text representation of estimators

estimator = CoxPHSurvivalAnalysis()
estimator.fit(data_x_numeric, data_y)

print(pd.Series(estimator.coef_, index=data_x_numeric.columns))