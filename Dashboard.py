import pandas as pd
import json
import os

# Load the data from CSV file
def process_student_data(csv_file_path='data/cleaned_resume_based_dataset.csv'):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Basic statistics
    stats = {
        'total_students': int(len(df)),
        'placed_students': int(df['placement'].sum()),
        'avg_cgpa': float(round(df['cgpa'].mean(), 2)),
        'with_internships': int(df['internships'].sum()),
        'with_projects': int(df['projects'].sum())
    }
    
    # Calculate placement rate
    stats['placement_rate'] = float(round((stats['placed_students'] / stats['total_students']) * 100, 1))
    
    # CGPA distribution
    cgpa_ranges = ['5.0-6.0', '6.1-7.0', '7.1-8.0', '8.1-9.0', '9.1-10.0']
    cgpa_bins = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    df['cgpa_range'] = pd.cut(df['cgpa'], bins=cgpa_bins, labels=cgpa_ranges, right=True)
    cgpa_distribution = df['cgpa_range'].value_counts().sort_index().to_dict()

    # Convert keys and values to regular types
    cgpa_distribution = {str(k): int(v) for k, v in cgpa_distribution.items()}
    
    # Skills distribution
    skill_cols = [col for col in df.columns if col.startswith('skill_')]
    skills_data = {}
    for skill in skill_cols:
        skill_name = skill.replace('skill_', '').upper()
        skills_data[skill_name] = int(df[skill].sum())
    
    # Placement by CGPA range
    placement_by_cgpa = {}
    for range_name in cgpa_ranges:
        range_df = df[df['cgpa_range'] == range_name]
        total = len(range_df)
        placed = range_df['placement'].sum()
        if total > 0:
            placement_by_cgpa[str(range_name)] = float(round((placed / total) * 100, 1))
        else:
            placement_by_cgpa[str(range_name)] = 0.0
    
    # Internship vs Placement
    internship_vs_placement = {
        'with_internship': {
            'placed': int(df[(df['internships'] == 1) & (df['placement'] == 1)].count()['placement']),
            'not_placed': int(df[(df['internships'] == 1) & (df['placement'] == 0)].count()['placement'])
        },
        'without_internship': {
            'placed': int(df[(df['internships'] == 0) & (df['placement'] == 1)].count()['placement']),
            'not_placed': int(df[(df['internships'] == 0) & (df['placement'] == 0)].count()['placement'])
        }
    }
    
    # Projects vs Placement
    projects_vs_placement = {
        'with_projects': {
            'placed': int(df[(df['projects'] == 1) & (df['placement'] == 1)].count()['placement']),
            'not_placed': int(df[(df['projects'] == 1) & (df['placement'] == 0)].count()['placement'])
        },
        'without_projects': {
            'placed': int(df[(df['projects'] == 0) & (df['placement'] == 1)].count()['placement']),
            'not_placed': int(df[(df['projects'] == 0) & (df['placement'] == 0)].count()['placement'])
        }
    }
    
    # Construct the final data object
    dashboard_data = {
        'stats': stats,
        'cgpa_distribution': cgpa_distribution,
        'skills_data': skills_data,
        'placement_by_cgpa': placement_by_cgpa,
        'internship_vs_placement': internship_vs_placement,
        'projects_vs_placement': projects_vs_placement
    }

    # Make sure directory exists
    os.makedirs('static/data', exist_ok=True)

    # Save to JSON with proper formatting
    with open('static/data/dashboard_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=4, default=str)

    return dashboard_data

# Run it if this file is executed directly
if __name__ == "__main__":
    data = process_student_data('data/cleaned_resume_based_dataset.csv')
    print("✅ Data processed successfully and saved to 'static/data/dashboard_data.json'")
