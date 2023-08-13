import pandas as pd 
import numpy as np 
import itertools
import functools
import operator
import pyqtgraph as pg 
import pingouin

df = pd.read_csv("dataset.csv", index_col=None)

#filters_var = ("Celltype", )
#groups = tuple(df[i].unique() for i in filters_var)
#for val_combo in itertools.product(*groups):
#    func = functools.reduce(operator.and_, (df[var].eq(value) for var, value in zip(filters_var, val_combo)))
#    #print(df[func])
#    print(val_combo, func)
#print(df.shape)

res = pingouin.anova(
    data=df, 
    dv="SurvivalDays", 
    between=["Treatment", "Status", "Age_in_years"], 
    effsize="n2", 
    detailed=True, 
    ss_type=2,
)
print(res)