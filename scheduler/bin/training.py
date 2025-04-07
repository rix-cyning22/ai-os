from sklearn.feature_selection import mutual_info_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

target = 'CPU usage [MHZ]'
df = pd.read_csv("bitbrains.csv")
features = df.columns.drop(['Timestamp [ms]', 'CPU usage [%]', target])
X = df[features]
y = df[target]
print(X.shape)
mi_scores = mutual_info_regression(X, y, random_state=42)
mi_scores = pd.Series(mi_scores, index=features).sort_values(ascending=False)

print("Mutual Information Scores:")
print(mi_scores)
top_features = mi_scores.index[:5].tolist()
print("\nTop features selected:", top_features)

X_selected = X[top_features]
X_train_val, X_test, y_train_val, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42)

print("\nDataset sizes:")
print("Train set:", X_train.shape)
print("Validation set:", X_val.shape)
print("Test set:", X_test.shape)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
print("the dataset has been scaled")
rf = RandomForestRegressor(random_state=42, max_depth=6)
rf.fit(X_train_scaled, y_train)

# -------------------------------
# 6. Evaluate the Model
# -------------------------------
# Evaluate on the training set
y_train_pred = rf.predict(X_train_scaled)
mae_train = mean_absolute_error(y_train, y_train_pred)
rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))
r2_train = r2_score(y_train, y_train_pred)
print("\nTraining Metrics:")
print("MAE: {:.3f}".format(mae_train))
print("RMSE: {:.3f}".format(rmse_train))
print("R2 Score: {:.3f}".format(r2_train))
# Evaluate on the validation set
y_val_pred = rf.predict(X_val_scaled)
mae_val = mean_absolute_error(y_val, y_val_pred)
rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))
r2_val = r2_score(y_val, y_val_pred)

print("\nValidation Metrics:")
print("MAE: {:.3f}".format(mae_val))
print("RMSE: {:.3f}".format(rmse_val))
print("R2 Score: {:.3f}".format(r2_val))

# Evaluate on the test set
y_test_pred = rf.predict(X_test_scaled)
mae_test = mean_absolute_error(y_test, y_test_pred)
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
r2_test = r2_score(y_test, y_test_pred)

print("\nTest Metrics:")
print("MAE: {:.3f}".format(mae_test))
print("RMSE: {:.3f}".format(rmse_test))
print("R2 Score: {:.3f}".format(r2_test))