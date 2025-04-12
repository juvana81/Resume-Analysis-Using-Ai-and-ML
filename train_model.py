# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Define feature list (should match resume_parser + feature_engineering)
skill_list = ['python', 'java', 'sql', 'ml', 'ai', 'html', 'css', 'c++', 'react', 'nodejs']
features = ['cgpa', 'internships', 'projects'] + [f'skill_{s}' for s in skill_list]

# Load consistent dataset
df = pd.read_csv('data/cleaned_resume_based_dataset.csv')  # Must contain only these features + Placement

# Make sure column names match exactly
expected_cols = features + ['placement']
if set(df.columns) != set(expected_cols):
    raise ValueError(f"Expected columns: {expected_cols}, but got: {list(df.columns)}")

# Split features & target
X = df[features]
y = df['placement']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model trained and saved successfully with matching features:")
print("   ", features)
