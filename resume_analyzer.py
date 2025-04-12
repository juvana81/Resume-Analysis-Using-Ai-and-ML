import os
import re
import json
import traceback
import PyPDF2
import docx2txt
import requests
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """
    Check if the file has an allowed extension
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'docx', 'doc'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text_from_resume(file_path):
    """
    Extract text from resume file (PDF or DOCX)
    """
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise Exception(f"PDF extraction error: {str(e)}")
    
    elif file_extension in ['docx', 'doc']:
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            raise Exception(f"DOCX extraction error: {str(e)}")
    
    else:
        raise Exception("Unsupported file format")

def extract_skills_from_text(text):
    """
    Extract potential skills from resume text using keyword matching
    """
    # Common technical skills (extend this list as needed)
    common_skills = [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
        'html', 'css', 'sql', 'nosql', 'mongodb', 'mysql', 'postgresql',
        'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'machine learning', 'deep learning', 'nlp', 'data science',
        'agile', 'scrum', 'devops', 'ci/cd', 'git', 'github'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Find skills in the text
    found_skills = []
    for skill in common_skills:
        # Use word boundary regex to match whole words
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
    
    return found_skills

def analyze_resume_with_mistral_ai(resume_text, api_key=None, api_url=None):
    """
    Enhanced resume analysis using Mistral AI API with focus on actionable feedback
    """
    if api_key is None:
        # Get from app config or environment variable
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            print("WARNING: No API key provided or found in environment variables")
            return {
                "error": True,
                "message": "Missing API key for Mistral AI"
            }
    
    if api_url is None:
        api_url = "https://api.mistral.ai/v1/chat/completions"
    
    # Enhanced prompt for Mistral AI
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and career coach. Analyze the following resume comprehensively and provide highly actionable feedback:
    
    RESUME TEXT:
    {resume_text}
    
    Provide your analysis with these specific sections:
    
    1. ATS COMPATIBILITY SCORE (0-100): Rate how well this resume would perform in ATS systems. Provide a numerical score and briefly explain why.
    
    2. KEY INFORMATION EXTRACTED:
       - Personal Details: Name, contact information (if available)
       - Education: Degrees, institutions, dates, GPA if mentioned
       - Skills: Technical skills, soft skills, tools, platforms
       - Experience: Summary of work history and key accomplishments
       - Projects: Notable projects mentioned
    
    3. STRENGTHS: List 3-5 specific strengths of this resume
    
    4. IMPROVEMENT OPPORTUNITIES: Provide 5 specific, actionable recommendations to improve this resume. Be detailed and concrete.
    
    5. SUITABLE JOB ROLES: Based on the skills and experience, list 3-5 specific job roles this person should consider applying for.
    
    6. SKILLS TO DEVELOP: Suggest 3-5 specific skills the candidate should develop to increase their marketability.
    
    7. RECOMMENDED CERTIFICATIONS: List 3-5 specific certifications that would complement their current profile.
    
    8. KEYWORD OPTIMIZATION: Suggest 5-10 keywords/phrases that should be included or emphasized for better ATS performance.
    
    Format your response with clear headings and bullet points for each section.
    Be specific, actionable, and tailored to the resume content.
    """
    
    # Request configuration
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "mistral-medium",  # Use appropriate model name
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,  # Lower temperature for more focused response
        "max_tokens": 1500
    }
    
    try:
        print("Sending request to Mistral AI API")
        response = requests.post(api_url, headers=headers, json=payload)
        
        print(f"API Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return {
                "error": True,
                "message": f"API returned error code {response.status_code}: {response.text}"
            }
        
        result = response.json()
        print(f"API Response received with {len(result.keys())} keys")
        print(f"API Response keys: {list(result.keys())}")
        
        # Extract and parse the AI's analysis
        if 'choices' in result and len(result['choices']) > 0:
            print(f"Choices count: {len(result['choices'])}")
            print(f"First choice keys: {list(result['choices'][0].keys())}")
            
            if 'message' in result['choices'][0]:
                print(f"Message keys: {list(result['choices'][0]['message'].keys())}")
                analysis = result['choices'][0]['message']['content']
                print(f"Successfully extracted analysis content (length: {len(analysis)})")
                print(f"Analysis preview: {analysis[:200]}...")  # Print beginning of response
                
                # Parse the raw text into structured sections
                parsed_result = parse_mistral_response(analysis)
                
                # For debugging, include the raw response
                parsed_result["raw_response"] = analysis
                
                return parsed_result
            else:
                print("No 'message' field found in the first choice")
                return {
                    "error": True,
                    "message": "Unexpected response format from Mistral AI: No message field"
                }
        else:
            print("No 'choices' field found in the response or it's empty")
            return {
                "error": True,
                "message": "Unexpected response format from Mistral AI: No choices found"
            }
    
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return {
            "error": True,
            "message": f"Failed to connect to Mistral AI: {str(e)}"
        }
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        traceback.print_exc()
        return {
            "error": True,
            "message": f"Resume analysis failed: {str(e)}"
        }

def parse_mistral_response(text):
    """
    Parse the raw text response from Mistral into structured sections
    """
    print("Starting to parse Mistral response")
    
    # Initialize with default empty values
    result = {
        "ats_score": None,
        "key_information": {
            "personal_details": [],
            "education": [],
            "skills": [],
            "experience": [],
            "projects": []
        },
        "strengths": [],
        "improvements": [],
        "suitable_roles": [],
        "skills_to_develop": [],
        "recommended_certs": [],
        "keywords": []
    }
    
    try:
        # Extract ATS score - simplified pattern
        ats_match = re.search(r'ATS COMPATIBILITY SCORE.*?(\d+)', text, re.IGNORECASE)
        if ats_match:
            result["ats_score"] = int(ats_match.group(1))
            print(f"Found ATS score: {result['ats_score']}")
        else:
            print("Could not find ATS score in the response")
            # Set a default score if not found
            result["ats_score"] = 60
        
        # Extract sections using simpler patterns
        # Extract personal details
        if "Personal Details:" in text:
            section = extract_section(text, "Personal Details:", ["Education:", "Skills:", "Experience:", "Projects:"])
            if section:
                result["key_information"]["personal_details"] = extract_bullet_points(section)
                print(f"Found {len(result['key_information']['personal_details'])} personal details")
        
        # Extract education
        if "Education:" in text:
            section = extract_section(text, "Education:", ["Skills:", "Experience:", "Projects:"])
            if section:
                result["key_information"]["education"] = extract_bullet_points(section)
                print(f"Found {len(result['key_information']['education'])} education items")
        
        # Extract skills
        if "Skills:" in text:
            section = extract_section(text, "Skills:", ["Experience:", "Projects:"])
            if section:
                result["key_information"]["skills"] = extract_bullet_points(section)
                print(f"Found {len(result['key_information']['skills'])} skills")
        
        # Extract experience
        if "Experience:" in text:
            section = extract_section(text, "Experience:", ["Projects:"])
            if section:
                result["key_information"]["experience"] = extract_bullet_points(section)
                print(f"Found {len(result['key_information']['experience'])} experience items")
        
        # Extract projects
        if "Projects:" in text:
            section = extract_section(text, "Projects:", ["STRENGTHS", "3.", "Strengths"])
            if section:
                result["key_information"]["projects"] = extract_bullet_points(section)
                print(f"Found {len(result['key_information']['projects'])} projects")
        
        # Extract strengths
        strengths_section = extract_major_section(text, ["STRENGTHS:", "3.", "Strengths:"], 
                                               ["IMPROVEMENT", "4.", "Improvement"])
        if strengths_section:
            result["strengths"] = extract_bullet_points(strengths_section)
            print(f"Found {len(result['strengths'])} strengths")
        
        # Extract improvements
        improvements_section = extract_major_section(text, ["IMPROVEMENT OPPORTUNITIES:", "4.", "Improvement:"], 
                                                  ["SUITABLE", "5.", "Suitable"])
        if improvements_section:
            result["improvements"] = extract_bullet_points(improvements_section)
            print(f"Found {len(result['improvements'])} improvements")
        
        # Extract suitable roles
        roles_section = extract_major_section(text, ["SUITABLE JOB ROLES:", "5.", "Suitable:"], 
                                           ["SKILLS TO", "6.", "Skills to"])
        if roles_section:
            result["suitable_roles"] = extract_bullet_points(roles_section)
            print(f"Found {len(result['suitable_roles'])} suitable roles")
        
        # Extract skills to develop
        skills_dev_section = extract_major_section(text, ["SKILLS TO DEVELOP:", "6.", "Skills to:"], 
                                                ["RECOMMENDED", "7.", "Recommended"])
        if skills_dev_section:
            result["skills_to_develop"] = extract_bullet_points(skills_dev_section)
            print(f"Found {len(result['skills_to_develop'])} skills to develop")
        
        # Extract recommended certifications
        certs_section = extract_major_section(text, ["RECOMMENDED CERTIFICATIONS:", "7.", "Recommended:"], 
                                           ["KEYWORD", "8.", "Keyword"])
        if certs_section:
            result["recommended_certs"] = extract_bullet_points(certs_section)
            print(f"Found {len(result['recommended_certs'])} recommended certifications")
        
        # Extract keywords
        keywords_section = extract_major_section(text, ["KEYWORD OPTIMIZATION:", "8.", "Keyword:"], [""])
        if keywords_section:
            result["keywords"] = extract_bullet_points(keywords_section)
            print(f"Found {len(result['keywords'])} keywords")

    except Exception as e:
        print(f"Error during parsing: {e}")
        traceback.print_exc()
    
    return result

def extract_section(text, start_marker, end_markers):
    """
    Extract a section from text between start_marker and any of the end_markers
    """
    try:
        # Find the start position
        start_pos = text.find(start_marker)
        if start_pos == -1:
            return None
        
        # Start after the marker
        start_pos += len(start_marker)
        
        # Find the earliest end marker
        end_pos = len(text)
        for marker in end_markers:
            marker_pos = text.find(marker, start_pos)
            if marker_pos != -1 and marker_pos < end_pos:
                end_pos = marker_pos
        
        # Extract the section
        section = text[start_pos:end_pos].strip()
        return section
    except Exception as e:
        print(f"Error extracting section {start_marker}: {e}")
        return None

def extract_major_section(text, start_markers, end_markers):
    """
    Extract a major section from text, trying multiple possible start and end markers
    """
    for start_marker in start_markers:
        start_pos = text.find(start_marker)
        if start_pos != -1:
            start_pos += len(start_marker)
            
            # Find the earliest end marker
            end_pos = len(text)
            for end_marker in end_markers:
                if end_marker:  # Skip empty end markers
                    marker_pos = text.find(end_marker, start_pos)
                    if marker_pos != -1 and marker_pos < end_pos:
                        end_pos = marker_pos
            
            section = text[start_pos:end_pos].strip()
            return section
    
    return None

def extract_bullet_points(text):
    """
    Extract bullet points from text, handling various bullet formats
    """
    if not text:
        return []
    
    # Split by common bullet point indicators and newlines
    items = []
    
    # First try to find bullet points with common markers
    bullet_matches = re.findall(r'(?:^|\n)(?:[-•*]|\d+\.)\s*(.*?)(?=(?:\n[-•*]|\n\d+\.|\Z))', text, re.DOTALL)
    
    if bullet_matches:
        items = [item.strip() for item in bullet_matches if item.strip()]
    else:
        # If no bullet points found, split by newlines
        items = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Clean up items (remove bullet points at start if any remain)
    cleaned_items = []
    for item in items:
        # Remove any leading bullet point or number that might remain
        cleaned = re.sub(r'^[-•*]|\d+\.\s*', '', item).strip()
        if cleaned:
            cleaned_items.append(cleaned)
    
    return cleaned_items