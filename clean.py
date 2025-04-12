import pandas as pd

# --- Step 1: Load the raw dataset safely ---
try:
    df = pd.read_csv("data/Sample.csv")  # Use forward slash for better cross-platform support
except FileNotFoundError:
    raise Exception("❌ File not found. Please make sure 'data/Sample.csv' exists!")

# --- Step 2: Normalize column names to avoid key errors ---
df.columns = df.columns.str.strip()

# --- Step 3: Map Yes/No columns to binary ---
binary_cols = ['Internships(Y/N)', 'Training(Y/N)', 'Innovative Project(Y/N)', 'Technical Course(Y/N)']
for col in binary_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.lower().map({'yes': 1, 'no': 0}).fillna(0).astype(int)
    else:
        df[col] = 0  # Add column if missing

# --- Step 4: Map 'Placement(Y/N)?' column to binary ---
if 'Placement(Y/N)?' in df.columns:
    df['placement'] = df['Placement(Y/N)?'].astype(str).str.strip().str.lower().map({'placed': 1, 'not placed': 0})
    df['placement'] = df['placement'].fillna(0).astype(int)
else:
    raise Exception("❌ Missing column: 'Placement(Y/N)?'")

# --- Step 5: Normalize CGPA column ---
if 'Cgpa' in df.columns:
    df.rename(columns={'Cgpa': 'cgpa'}, inplace=True)
else:
    raise Exception("❌ Missing column: 'Cgpa'")

# --- Step 6: Add skill features ---
all_skills = ['python', 'java', 'sql', 'ml', 'ai', 'html', 'css', 'c++', 'react', 'nodejs']
for skill in all_skills:
    df[f'skill_{skill}'] = 0  # default to 0, can be filled later via parser

# --- Step 7: Example - manually add some dummy skills (demo only) ---
# Simulate real resume parsing here
if len(df) > 0:
    df.loc[0, ['skill_python', 'skill_sql', 'skill_ml']] = 1
if len(df) > 1:
    df.loc[1, ['skill_java', 'skill_html', 'skill_css']] = 1
if len(df) > 2:
    df.loc[2, ['skill_python', 'skill_ai', 'skill_sql']] = 1
if len(df) > 3:
    df.loc[3, ['skill_python', 'skill_html', 'skill_css']] = 1

# --- Step 8: Add 'projects' column ---
if 'Innovative Project(Y/N)' in df.columns:
    df['projects'] = df['Innovative Project(Y/N)']
else:
    df['projects'] = 0

# --- Step 9: Select final features ---
selected_features = ['cgpa', 'Internships(Y/N)', 'projects'] + [f'skill_{s}' for s in all_skills] + ['placement']

# Ensure all selected columns exist in DataFrame
missing_cols = [col for col in selected_features if col not in df.columns]
if missing_cols:
    raise Exception(f"❌ Missing columns in dataset: {missing_cols}")

final_df = df[selected_features].copy()

# --- Step 10: Rename internship column for compatibility ---
final_df.rename(columns={'Internships(Y/N)': 'internships'}, inplace=True)

# --- Step 11: Save cleaned dataset ---
final_df.to_csv("data/cleaned_resume_based_dataset.csv", index=False)
print("✅ Dataset cleaned and saved as 'data/cleaned_resume_based_dataset.csv'")
