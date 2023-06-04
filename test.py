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
df = OneHotEncoder().fit_transform(df)

x = tuple(zip(df["SurvivalDays"], df["Status"]))
print(data_y, type(data_y), data_y.dtype)
#data_x_numeric = OneHotEncoder().fit_transform(data_x)

#set_config(display="text")  # displays text representation of estimators

estimator = CoxPHSurvivalAnalysis()
estimator.fit(data_x_numeric, data_y)
#print(pd.Series(estimator.coef_, index=data_x_numeric.columns))


def fit_and_score_features(X, y):
    n_features = X.shape[1]
    scores = np.empty(n_features)
    m = CoxPHSurvivalAnalysis()
    for j in range(n_features):
        Xj = X[:, j:j+1]
        m.fit(Xj, y)
        scores[j] = m.score(Xj, y)
    return scores

scores = fit_and_score_features(data_x_numeric.values, data_y)
#print(scores)
#print(pd.Series(scores, index=data_x_numeric.columns).sort_values(ascending=False))






"""
from sksurv.metrics import concordance_index_censored

prediction = estimator.predict(data_x_numeric)
result = concordance_index_censored(data_y["Status"], data_y["Survival_in_days"], prediction)
print(result) #[0]
"""
