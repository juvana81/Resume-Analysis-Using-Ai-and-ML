import re

def parse_resume(file_path):
    import fitz  # PyMuPDF
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # Basic skill matching using a predefined list
    skill_keywords = [
        'python', 'java', 'c++', 'sql', 'html', 'css', 'javascript',
        'react', 'node.js', 'flask', 'django', 'excel', 'ml', 'ai',
        'tensorflow', 'keras', 'pandas', 'numpy', 'matplotlib',
        'data analysis', 'power bi', 'tableau'
    ]

    text_lower = text.lower()
    found_skills = [skill for skill in skill_keywords if skill in text_lower]

    return {
        'text': text,
        'skills': found_skills
    }

