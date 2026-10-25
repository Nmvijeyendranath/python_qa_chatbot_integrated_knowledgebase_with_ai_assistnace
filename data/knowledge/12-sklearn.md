# scikit-learn Fundamentals and Machine Learning Workflows

Source: https://scikit-learn.org/stable/user_guide.html

## What is scikit-learn?

scikit-learn is the standard Python library for classical machine learning. It provides:
- Consistent API: `fit()`, `predict()`, `transform()`
- Classification, regression, clustering, dimensionality reduction
- Model selection (cross-validation, hyperparameter search)
- Preprocessing pipelines

```bash
pip install scikit-learn
```

```python
import sklearn
print(sklearn.__version__)
```

## The Estimator API

Every scikit-learn model follows the same interface:

```python
# 1. Import the estimator
from sklearn.linear_model import LogisticRegression

# 2. Instantiate with hyperparameters
model = LogisticRegression(max_iter=1000, random_state=42)

# 3. Fit on training data
model.fit(X_train, y_train)

# 4. Predict on new data
predictions = model.predict(X_test)

# 5. Evaluate
score = model.score(X_test, y_test)   # accuracy for classifiers
```

## A Complete Workflow Example

```python
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# 1. Load data
iris = load_iris()
X = iris.data    # shape (150, 4)
y = iris.target  # shape (150,)

# 2. Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Preprocess
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)   # fit on train, transform both
X_test  = scaler.transform(X_test)        # DO NOT fit on test data

# 4. Train
model = LogisticRegression(max_iter=200, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

## Preprocessing

```python
from sklearn.preprocessing import (
    StandardScaler,    # mean=0, std=1
    MinMaxScaler,      # scale to [0, 1]
    RobustScaler,      # robust to outliers
    LabelEncoder,      # encode target labels
    OneHotEncoder,     # encode categorical features
    OrdinalEncoder,
)
from sklearn.impute import SimpleImputer

# Standardise features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# One-hot encode categorical features
encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
X_encoded = encoder.fit_transform(X_categorical)

# Impute missing values
imputer = SimpleImputer(strategy="mean")   # or "median", "most_frequent"
X_imputed = imputer.fit_transform(X_with_nan)
```

## Pipelines

Pipelines chain preprocessing and model steps to prevent data leakage:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("svm",    SVC(kernel="rbf", C=1.0)),
])

pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
score = pipe.score(X_test, y_test)
```

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

# Handle mixed numeric + categorical data
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
])

pipeline = Pipeline([
    ("prep",  preprocessor),
    ("model", RandomForestClassifier(n_estimators=100, random_state=42)),
])

pipeline.fit(X_train, y_train)
```

## Common Algorithms

### Classification

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# All share the same API
for name, clf in [
    ("LR",  LogisticRegression(max_iter=1000)),
    ("RF",  RandomForestClassifier(n_estimators=100)),
    ("SVM", SVC()),
]:
    clf.fit(X_train, y_train)
    print(f"{name}: {clf.score(X_test, y_test):.4f}")
```

### Regression

```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

model = Ridge(alpha=1.0)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"MSE: {mean_squared_error(y_test, y_pred):.4f}")
print(f"R²:  {r2_score(y_test, y_pred):.4f}")
```

### Clustering

```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)
print(f"Silhouette score: {silhouette_score(X, labels):.4f}")
print(kmeans.cluster_centers_)
```

## Model Selection and Cross-Validation

```python
from sklearn.model_selection import (
    cross_val_score,
    StratifiedKFold,
    GridSearchCV,
    RandomizedSearchCV,
)

# K-fold cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

# Grid search for hyperparameter tuning
param_grid = {
    "model__C": [0.01, 0.1, 1, 10],
    "model__kernel": ["linear", "rbf"],
}
grid = GridSearchCV(pipeline, param_grid, cv=5, scoring="accuracy", n_jobs=-1)
grid.fit(X_train, y_train)
print(f"Best params: {grid.best_params_}")
print(f"Best score:  {grid.best_score_:.4f}")
best_model = grid.best_estimator_
```

## Evaluation Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve,
    mean_squared_error, r2_score, mean_absolute_error,
)

# Classification metrics
print(accuracy_score(y_test, y_pred))
print(precision_score(y_test, y_pred, average="weighted"))
print(recall_score(y_test, y_pred, average="weighted"))
print(f1_score(y_test, y_pred, average="weighted"))
print(confusion_matrix(y_test, y_pred))

# ROC-AUC (binary classification)
proba = model.predict_proba(X_test)[:, 1]
print(roc_auc_score(y_test, proba))

# Regression metrics
print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, y_pred):.4f}")
print(f"R²:   {r2_score(y_test, y_pred):.4f}")
```

## Saving and Loading Models

```python
import joblib

# Save
joblib.dump(pipeline, "model.joblib")

# Load
loaded_pipeline = joblib.load("model.joblib")
loaded_pipeline.predict(X_new)
```

## Feature Importance and Inspection

```python
# Tree-based models
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

importances = rf.feature_importances_
for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
    print(f"{name}: {imp:.4f}")

# Linear models — coefficients
lr = LogisticRegression().fit(X_train, y_train)
print(lr.coef_)

# Inspect pipeline steps
print(pipeline.named_steps["scaler"].mean_)
print(pipeline.named_steps["model"].feature_importances_)
```

## Common scikit-learn Mistakes

```python
# Data leakage: fitting scaler on entire dataset before splitting
scaler.fit(X)           # BUG — includes test data
X_train = scaler.transform(X_train)

# Correct: fit on train only
X_train, X_test = train_test_split(X, ...)
scaler.fit(X_train)     # OK
X_train = scaler.transform(X_train)
X_test  = scaler.transform(X_test)
# Better: use Pipeline — it handles this automatically

# Using score() before fit()
model.score(X_test, y_test)   # NotFittedError
model.fit(X_train, y_train)   # fit first!

# Using wrong scoring for imbalanced data
cross_val_score(model, X, y, scoring="accuracy")  # misleading for imbalanced
cross_val_score(model, X, y, scoring="f1_macro")  # better for imbalanced
```

## Frequently Asked Questions

**Q: What is the difference between `fit_transform()` and `transform()`?**
`fit_transform()` learns parameters (e.g., mean, std) from data and transforms it in one step. Use it on training data. `transform()` applies learned parameters to new data without refitting. Always use `transform()` on test/validation data.

**Q: Why should I use `Pipeline` instead of transforming data manually?**
Pipelines prevent data leakage (the preprocessor is refitted only on training folds during cross-validation), make code cleaner, and allow grid-searching over preprocessing hyperparameters.

**Q: How do I handle class imbalance?**
Options: `class_weight="balanced"` parameter in the estimator; oversample minority class (`SMOTE` from `imbalanced-learn`); undersample majority class; use appropriate metrics (F1, AUC) instead of accuracy.

**Q: What is the difference between `predict()` and `predict_proba()`?**
`predict()` returns the class label (e.g., 0 or 1). `predict_proba()` returns the probability for each class (shape: [n_samples, n_classes]). Use `predict_proba()` for ROC curves and calibrated thresholds.
