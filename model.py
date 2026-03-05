import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score

# Load dataset
df = pd.read_csv("insurance.csv")

# Features and target
X = df.drop("charges", axis=1)
y = df["charges"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Categorical and numerical columns
categorical_features = ["sex", "smoker", "region"]
numerical_features = ["age", "bmi", "children"]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(drop="first"), categorical_features),
        ("num", "passthrough", numerical_features)
    ]
)

# Create Pipeline
pipeline = Pipeline([
    ("preprocessing", preprocessor),
    ("model", RandomForestRegressor(random_state=42))
])

# Train pipeline
pipeline.fit(X_train, y_train)

# Predict
y_pred = pipeline.predict(X_test)

# Evaluate
r2 = r2_score(y_test, y_pred)
print("Model R2 Score:", r2)

# Save pipeline model
pickle.dump(pipeline, open("model.pkl", "wb"))
pickle.dump(r2, open("accuracy.pkl", "wb"))

print("Pipeline model saved successfully!")