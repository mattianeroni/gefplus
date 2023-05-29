from sksurv.datasets import load_veterans_lung_cancer
import pandas as pd 
import numpy as np 
import pingouin as pg


df = pd.read_csv("results.csv")


#df = pg.read_dataset('mixed_anova')

# Run the ANOVA
aov = pg.anova(data=df, dv="SurvivalDays", between=('Age_in_years', "Karnofsky_score"), detailed=True)
print(aov)