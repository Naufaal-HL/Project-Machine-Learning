# -*- coding: utf-8 -*-
"""ML_LANJUT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19SBJa2AYLxvbxUNcZcOKIguny0G3E7k5

# **Tugas Besar Pembelajaran Mesin Lanjut**

1. Naufal Haritsah Luthfi        - 1301194073
>
2. Firdaus Putra Kurniyanto      - 1301190385

>
>

##**Import Library**
"""

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.impute import SimpleImputer
from sklearn import preprocessing

from niapy.problems import Problem
from niapy.task import OptimizationType, Task
from niapy.algorithms.modified import HybridBatAlgorithm
from niapy.algorithms.basic import ParticleSwarmOptimization

import numpy as np
import pandas as pd
import random
import warnings
warnings.filterwarnings('ignore')

"""##**Import Dataset**"""

df = pd.read_csv('./dataset/BostonData.csv')

df.head()

"""##**PREPROCESSING**

**CHECK DUPLICATE DATA**
"""

df.duplicated().sum()

df.isna().sum()

"""**MENGISI MISSING VALUE**"""

x = df.values
#Mendefinisikan strategi yang digunakan untuk mengisi value yang hilang,
#disini menggunakan mean
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
imputer.fit(x[:, 2:3])
x[:, 2:3] = imputer.transform(x[:, 2:3])
imputer.fit(x[:, 8:-1])
x[:, 8:-1] = imputer.transform(x[:, 8:-1])
#Mengubah list array menjadi dataframe
names = df.columns
df = pd.DataFrame(x, columns=names)
#Mengisi missing value dengan strategi modus, atau value yang sering muncul
df = df.fillna(df.mode().iloc[0])
df.head()

df.isna().sum()

df.describe()

"""**NORMALIZATION**"""

names = df.columns
scaler = preprocessing.MinMaxScaler()
d = scaler.fit_transform(df)
df = pd.DataFrame(d, columns=names)
df.head()

"""###**DATA SPLITTING**"""

X = df.drop('PRICE', axis=1)
feature_names = X .columns
X = X.to_numpy()
y = df['PRICE']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)

"""##**SVR**

###**FEATURE SELECTION**
"""

class SVRFeatureSelection(Problem):
    def __init__(self, X_train, y_train, alpha=0.99):
        super().__init__(dimension=X_train.shape[1], lower=0, upper=1)
        self.X_train = X_train
        self.y_train = y_train
        self.alpha = alpha

    def _evaluate(self, x):
        selected = x > 0.5
        num_selected = selected.sum()
        if num_selected == 0:
            return 1.0
        accuracy = cross_val_score(
            SVR(), self.X_train[:, selected], self.y_train, cv=2, n_jobs=-1).mean()
        score = 1 - accuracy
        num_features = self.X_train.shape[1]
        return self.alpha * score + (1 - self.alpha) * (num_selected / num_features)

problem = SVRFeatureSelection(X_train, y_train)
task = Task(problem, max_iters=100)
algorithm = ParticleSwarmOptimization(population_size=10, seed=1234)
best_features, best_fitness = algorithm.run(task)

selected_features = best_features > 0.5
print('Number of selected features:', selected_features.sum())
print('Selected features:', ', '.join(
    feature_names[selected_features].tolist()))

"""###**Eksperimen SVR**"""

model_selected = SVR()
model_all = SVR()
model_selected.fit(X_train[:, selected_features], y_train)
print('Subset accuracy:', model_selected.score(
    X_test[:, selected_features], y_test))

model_all.fit(X_train, y_train)
print('All Features Accuracy:', model_all.score(X_test, y_test))

"""##**KNR**

###**FEATURE SELECTION**
"""

class KNRFeatureSelection(Problem):
    def __init__(self, X_train, y_train, alpha=0.99):
        super().__init__(dimension=X_train.shape[1], lower=0, upper=1)
        self.X_train = X_train
        self.y_train = y_train
        self.alpha = alpha

    def _evaluate(self, x):
        selected = x > 0.5
        num_selected = selected.sum()
        if num_selected == 0:
            return 1.0
        accuracy = cross_val_score(
            KNeighborsRegressor(), self.X_train[:, selected], self.y_train, cv=2, n_jobs=-1).mean()
        score = 1 - accuracy
        num_features = self.X_train.shape[1]
        return self.alpha * score + (1 - self.alpha) * (num_selected / num_features)

problem = KNRFeatureSelection(X_train, y_train)
task = Task(problem, max_iters=100)
algorithm = ParticleSwarmOptimization(population_size=10, seed=1234)
best_features, best_fitness = algorithm.run(task)

selected_features = best_features > 0.5
print('Number of selected features:', selected_features.sum())
print('Selected features:', ', '.join(
    feature_names[selected_features].tolist()))

"""###**Eksperimen KNR**"""

model_selected = KNeighborsRegressor()
model_all = KNeighborsRegressor()
model_selected.fit(X_train[:, selected_features], y_train)
print('Subset accuracy:', model_selected.score(
    X_test[:, selected_features], y_test))

model_all.fit(X_train, y_train)
print('All Features Accuracy:', model_all.score(X_test, y_test))

"""##**TUNING SVR**"""

def get_hyperparameters(x):
    """Get hyperparameters for solution `x`."""
    gamma = (1, 0.1, 0.01, 0.001, 0.0001)
    c = (0.1, 1, 10, 100, 1000)

    params = {
        'gamma':gamma[int(x[0]*3)],
        'C':  c[int(x[1]*1)],
    }
    return params


def get_classifier(x):
    """Get classifier from solution `x`."""
    params = get_hyperparameters(x)
    return SVR(**params)

class SVRHyperparameterOptimization(Problem):
    def __init__(self, X_train, y_train):
        super().__init__(dimension=4, lower=0, upper=1)
        self.X_train = X_train
        self.y_train = y_train

    def _evaluate(self, x):
        model = get_classifier(x)
        scores = cross_val_score(
            model, self.X_train, self.y_train, cv=2, n_jobs=-1)
        return scores.mean()

def optimization_model(method):
    problem = SVRHyperparameterOptimization(X_train, y_train)

    # We will be running maximization for 100 iters on `problem`
    task = Task(problem, max_iters=100,
                optimization_type=OptimizationType.MAXIMIZATION)

    algorithm = method(population_size=10, seed=1234)
    best_params, _ = algorithm.run(task)

    print('Best parameters:', get_hyperparameters(best_params))
    return best_params

def optimization(model):
    best_params = optimization_model(model)
    tuned_model_selected_feature = get_classifier(best_params)
    tuned_model_all_feature = get_classifier(best_params)

    tuned_model_selected_feature.fit(X_train[:, selected_features], y_train)
    print('Subset accuracy:', tuned_model_selected_feature.score(
        X_test[:, selected_features], y_test))

    tuned_model_all_feature.fit(X_train, y_train)
    print('All Features Accuracy:', tuned_model_all_feature.score(X_test, y_test))

"""**Particle Swarm Optimization**"""

optimization(ParticleSwarmOptimization)

"""**Hybrid Bat Algorithm**"""

optimization(HybridBatAlgorithm)

"""##**TUNING KNR**"""

def get_hyperparameters(x):
    """Get hyperparameters for solution `x`."""
    algorithms = ('ball_tree', 'kd_tree', 'brute')
    n_neighbors = int(5 + x[0] * 10)
    weights = 'uniform' if x[1] < 0.5 else 'distance'
    algorithm = algorithms[int(x[2] * 2)]
    leaf_size = int(10 + x[3] * 40)

    params = {
        'n_neighbors': n_neighbors,
        'weights': weights,
        'algorithm': algorithm,
        'leaf_size': leaf_size
    }
    return params


def get_classifier(x):
    """Get classifier from solution `x`."""
    params = get_hyperparameters(x)
    return KNeighborsRegressor(**params)

class KNRHyperparameterOptimization(Problem):
    def __init__(self, X_train, y_train):
        super().__init__(dimension=4, lower=0, upper=1)
        self.X_train = X_train
        self.y_train = y_train

    def _evaluate(self, x):
        model = get_classifier(x)
        scores = cross_val_score(
            model, self.X_train, self.y_train, cv=2, n_jobs=-1)
        return scores.mean()

def optimization_model_knr(method):
    problem = KNRHyperparameterOptimization(X_train, y_train)

    # We will be running maximization for 100 iters on `problem`
    task = Task(problem, max_iters=100,
                optimization_type=OptimizationType.MAXIMIZATION)

    algorithm = method(population_size=10, seed=1234)
    best_params, _ = algorithm.run(task)

    print('Best parameters:', get_hyperparameters(best_params))
    return best_params

def optimization_knr(model):
    best_params = optimization_model_knr(model)
    tuned_model_selected_feature = get_classifier(best_params)
    tuned_model_all_feature = get_classifier(best_params)

    tuned_model_selected_feature.fit(X_train[:, selected_features], y_train)
    print('Subset accuracy:', tuned_model_selected_feature.score(
        X_test[:, selected_features], y_test))

    tuned_model_all_feature.fit(X_train, y_train)
    print('All Features Accuracy:', tuned_model_all_feature.score(X_test, y_test))

optimization_knr(ParticleSwarmOptimization)

optimization_knr(HybridBatAlgorithm)