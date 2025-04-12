def convert_to_features(profile, label_encoders):
    cgpa = float(profile['cgpa'])
    internships = int(profile['internships'])
    projects = int(profile['projects'])
    skills = profile['skills']

    # Skill keywords expected by the model
    skill_keywords = ['python', 'java', 'sql', 'ml', 'ai', 'html', 'css', 'c++', 'react', 'nodejs']

    # Create skill features
    skill_features = []
    for skill in skill_keywords:
        skill_features.append(1 if skill.lower() in [s.lower() for s in skills] else 0)

    return [cgpa, internships, projects] + skill_features

