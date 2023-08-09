import pandas as pd 
import numpy as np 
import itertools
import functools
import operator
import pyqtgraph as pg 

df = pd.read_csv("dataset.csv", index_col=None)

filters_var = ("Celltype", )
groups = tuple(df[i].unique() for i in filters_var)

for val_combo in itertools.product(*groups):
    func = functools.reduce(operator.and_, (df[var].eq(value) for var, value in zip(filters_var, val_combo)))
    #print(df[func])
    print(val_combo, func)
