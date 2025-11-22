import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import  mean_absolute_error, mean_squared_error
import pickle
import Credit_Score_Predictor as cs


X = cs.Output_Data
y = cs.finaldata

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=18,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
pred = model.predict(X_test)


print("Mean_Absoulte_Error:", mean_absolute_error(y_test, pred))
print("Mean_Square_Error:", np.sqrt(mean_squared_error(y_test, pred)))


