import pandas as pd
from matplotlib import pyplot as plt
import ast
import numpy as np

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic, ExpSineSquared, DotProduct
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, root_mean_squared_error
import numpy as np
from skopt import BayesSearchCV
from sklearn.preprocessing import StandardScaler

# Load training and testing datasets
train_df = pd.read_csv('train.csv')
test_df = pd.read_csv('test.csv')

# Data preprocessing through standardization

scaler = StandardScaler()

X_train_original = train_df[['vo', 'vs', 'vo_c']]
y_train = train_df[['dc']]

X_test_original = test_df[['vo', 'vs', 'vo_c']]
y_test = test_df[['dc']]

X_train = scaler.fit_transform(X_train_original)
X_test = scaler.transform(X_test_original)

# Training using Bayesian optimization

opt = BayesSearchCV(
    GaussianProcessRegressor(kernel=Matern()),
    search_spaces = {
                    'alpha': (1e-4, 1, 'log-uniform'), 
                     'normalize_y': [True, False], 
                     'copy_X_train': [True, False], 
                     'n_restarts_optimizer': (0, 20),
                     }
)
opt.fit(X_train, y_train)
gpr = opt.best_estimator_

# Testing trained GPR model with test dataset

y_pred = gpr.predict(X_test)
print('MSE:', mean_squared_error(y_test, y_pred))
print('RMSE:', root_mean_squared_error(y_test, y_pred))
print('MAE:', mean_absolute_error(y_test, y_pred))
print('R2 score:', r2_score(y_test, y_pred))

# Save trained gpr model and scaler

from joblib import dump, load

dump(gpr, 'gpr l2 1k dc.joblib')
dump(scaler, 'scaler l2 1k dc.pkl')