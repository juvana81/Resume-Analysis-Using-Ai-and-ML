import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # For non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import tempfile
import requests
import json
from werkzeug.utils import secure_filename
import PyPDF2
import docx2txt
import re
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from resume_analyzer import extract_text_from_resume, analyze_resume_with_mistral_ai, allowed_file, extract_skills_from_text
# Import utility modules
from utils.resume_parser import parse_resume
from utils.feature_engineering import convert_to_features
import os
import traceback
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
# Import functions from resume_analyzer module
# Create this file using your provided resume_analyzer code
app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'

from flask_session import Session
Session(app)


app.secret_key = 'placement_predictor_secret_key'  # Required for flash messages and sessions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CHART_FOLDER'] = 'static/charts'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Add Mistral API Configuration
app.config['MISTRAL_API_KEY'] = ""  # Replace with your actual API key
app.config['MISTRAL_API_URL'] = "https://api.mistral.ai/v1/chat/completions"
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)

# Load ML model and encoders
try:
    model = pickle.load(open('model/model.pkl', 'rb'))
    label_encoders = pickle.load(open('model/label_encoders.pkl', 'rb'))
    print("Model and encoders loaded successfully")
except Exception as e:
    print(f"Error loading model or encoders: {e}")
    # Create dummy model and encoders for development if needed
    model = None
    label_encoders = {}

# Reference data (for charts comparison)
reference_data = {
    'average_cgpa': 7.5,
    'average_internships': 1.2,
    'average_projects': 3.5,
    'placed_cgpa_avg': 8.1,
    'placed_internships_avg': 1.8,
    'placed_projects_avg': 4.2,
    'popular_skills': {
        'Python': 85,
        'Java': 65,
        'SQL': 60,
        'HTML/CSS': 55,
        'JavaScript': 50,
        'Machine Learning': 45,
        'Data Analytics': 40,
        'Cloud Computing': 30,
        'Mobile Development': 25
    }
}

# Global session state variables
@app.before_request
def before_request():
    if 'resume_text' not in session:
        session['resume_text'] = ""
    if 'resume_skills' not in session:
        session['resume_skills'] = []

# ---------- Helper functions ----------
def generate_skills_chart(user_skills):
    """Generate a chart comparing user skills with industry demand"""
    plt.figure(figsize=(10, 6))
    
    # Data preparation
    all_skills = list(reference_data['popular_skills'].keys())
    user_has_skill = [1 if skill in user_skills else 0 for skill in all_skills]
    industry_demand = [reference_data['popular_skills'][skill]/100 for skill in all_skills]
    
    # Create chart
    x = np.arange(len(all_skills))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    rects1 = ax.bar(x - width/2, user_has_skill, width, label='Your Skills', color='#7b1fa2')
    rects2 = ax.bar(x + width/2, industry_demand, width, label='Industry Demand', color='#e1bee7')
    
    # Add labels and formatting
    ax.set_title('Your Skills vs Industry Demand', fontsize=16)
    ax.set_ylabel('Presence / Demand Level', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(all_skills, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value annotations
    for rect in rects1:
        height = rect.get_height()
        if height > 0:
            ax.annotate('Yes', xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')
    
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{int(height*100)}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save chart
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{app.config['CHART_FOLDER']}/skills_chart_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
    
    return filename

def generate_cgpa_comparison(user_cgpa):
    """Generate a chart comparing user's CGPA with averages"""
    user_cgpa = float(user_cgpa)
    
    categories = ['Your CGPA', 'Average CGPA', 'Avg. CGPA (Placed Students)']
    values = [user_cgpa, reference_data['average_cgpa'], reference_data['placed_cgpa_avg']]
    colors = ['#7b1fa2' if i == 0 else '#9c27b0' for i in range(len(categories))]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, values, color=colors)
    plt.axhline(y=reference_data['placed_cgpa_avg'], color='red', linestyle='--', alpha=0.7, 
                label=f"Placement Threshold ({reference_data['placed_cgpa_avg']})")
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}', ha='center', va='bottom')
    
    plt.title('CGPA Comparison', fontsize=16)
    plt.ylabel('CGPA (out of 10)', fontsize=12)
    plt.ylim(0, 10.5)  # Set y-axis limit for CGPA scale
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Save chart
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{app.config['CHART_FOLDER']}/cgpa_chart_{timestamp}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    
    return filename

def generate_experience_chart(internships, projects):
    """Generate a chart showing impact of experience"""
    internships = int(internships)
    projects = int(projects)
    
    categories = ['Internships', 'Projects']
    your_values = [internships, projects]
    avg_values = [reference_data['average_internships'], reference_data['average_projects']]
    placed_values = [reference_data['placed_internships_avg'], reference_data['placed_projects_avg']]
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width, your_values, width, label='Your Experience', color='#7b1fa2')
    rects2 = ax.bar(x, avg_values, width, label='Average', color='#9c27b0')
    rects3 = ax.bar(x + width, placed_values, width, label='Placed Students', color='#e1bee7')
    
    # Add labels and formatting
    ax.set_title('Experience Comparison', fontsize=16)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value annotations
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save chart
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{app.config['CHART_FOLDER']}/experience_chart_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
    
    return filename

def generate_recommendations(cgpa, internships, projects, skills, prediction_result):
    """Generate personalized recommendations based on profile"""
    recommendations = []
    cgpa = float(cgpa)
    internships = int(internships)
    projects = int(projects)
    
    # CGPA recommendations
    if cgpa < reference_data['placed_cgpa_avg']:
        gap = reference_data['placed_cgpa_avg'] - cgpa
        recommendations.append(f"Focus on improving your academic performance. Aim to increase your CGPA by at least {gap:.1f} points to match the average of placed students.")
    
    # Internship recommendations
    if internships < reference_data['placed_internships_avg']:
        recommendations.append(f"Consider taking on more internships. Placed students have an average of {reference_data['placed_internships_avg']} internships.")
    
    # Project recommendations
    if projects < reference_data['placed_projects_avg']:
        recommendations.append(f"Work on more projects to demonstrate your applied skills. Try to complete at least {int(reference_data['placed_projects_avg']) - projects} more projects.")
    
    # Skills recommendations
    missing_popular_skills = []
    for skill, popularity in reference_data['popular_skills'].items():
        if popularity > 50 and skill not in skills:
            missing_popular_skills.append(skill)
    
    if missing_popular_skills:
        recommendations.append(f"Consider learning these in-demand skills: {', '.join(missing_popular_skills[:3])}.")
    
    # Generic recommendations if needed
    if not recommendations:
        if prediction_result['prediction'] == 'You are Likely to be Placed':
            recommendations.append("Your profile is strong. Consider taking on leadership roles to further enhance your resume.")
            recommendations.append("Start preparing for technical interviews and aptitude tests early.")
        else:
            recommendations.append("Focus on practical applications of your skills through personal projects.")
            recommendations.append("Consider participating in hackathons or coding competitions to stand out.")
    
    return recommendations

# ---------- Routes ----------
@app.route('/')
def home():
    # Clear any existing session data
    session.clear()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home'))
    
    resume = request.files['resume']
    
    if resume.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home'))
    
    if resume:
        try:
            # Save the uploaded file
            filename = f"resume_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(path)
            
            # Parse the resume
            parsed_resume = parse_resume(path)
            session['resume_text'] = parsed_resume['text']
            session['resume_skills'] = parsed_resume['skills']
            
            print(f"Extracted {len(session['resume_skills'])} skills from resume")
            
            return render_template('result.html', 
                                  resume_text=session['resume_text'], 
                                  show_input=True)
        
        except Exception as e:
            print(f"Error processing resume: {e}")
            flash(f"Error processing resume: {str(e)}", 'error')
            return redirect(url_for('home'))
    
    return redirect(url_for('home'))

@app.route('/input')
def input_form():
    return render_template('result.html', 
                          resume_text=session.get('resume_text', ''), 
                          show_input=True)

@app.route('/result', methods=['POST'])
def result():
    try:
        # Get form data
        cgpa = request.form.get('cgpa')
        internships = request.form.get('internships')
        projects = request.form.get('projects')
        selected_skills = request.form.getlist('skills')
        
        # Input validation
        if not all([cgpa, internships, projects]):
            flash("Please fill all required fields", "error")
            return redirect(url_for('input_form'))
        
        try:
            cgpa = float(cgpa)
            if not (0 <= cgpa <= 10):
                flash("CGPA must be between 0 and 10", "error")
                return redirect(url_for('input_form'))
        except ValueError:
            flash("CGPA must be a number", "error")
            return redirect(url_for('input_form'))
        
        try:
            internships = int(internships)
            projects = int(projects)
            if internships < 0 or projects < 0:
                flash("Number of internships and projects cannot be negative", "error")
                return redirect(url_for('input_form'))
        except ValueError:
            flash("Number of internships and projects must be integers", "error")
            return redirect(url_for('input_form'))
        
        # Combine resume and selected skills
        resume_skills = session.get('resume_skills', [])
        all_skills = list(set(resume_skills + selected_skills))
        
        # Create profile
        profile = {
            'cgpa': cgpa,
            'internships': internships,
            'projects': projects,
            'skills': all_skills
        }
        
        # Feature engineering and prediction
        prediction_result = {}
        if model:
            # Convert profile to features
            features = convert_to_features(profile, label_encoders)
            
            # Prepare input for model
            columns = ['cgpa', 'internships', 'projects', 'skill_python', 'skill_java', 'skill_sql',
                       'skill_ml', 'skill_ai', 'skill_html', 'skill_css', 'skill_c++',
                       'skill_react', 'skill_nodejs']
            
            input_df = pd.DataFrame([features], columns=columns)
            
            # Make prediction
            prediction = model.predict(input_df)[0]
            prediction_label = 'You are Likely to be Placed' if prediction == 1 else 'You are Likely to be Not Placed'
            prediction_proba = model.predict_proba(input_df)[0][1]
            
            prediction_result = {
                'prediction': prediction_label,
                'probability': round(prediction_proba * 100, 2)
            }
        else:
            # If model is not available, use a dummy prediction
            print("Using dummy prediction as model is not available")
            prediction_result = {
                'prediction': 'You are Likely to be Placed' if cgpa >= 7.5 else 'You are Likely to be Not Placed',
                'probability': 85 if cgpa >= 7.5 else 45
            }
        
        # Generate charts
        charts = {
            'skills_chart': generate_skills_chart(all_skills),
            'cgpa_chart': generate_cgpa_comparison(cgpa),
            'experience_chart': generate_experience_chart(internships, projects)
        }
        
        # Generate recommendations
        recommendations = generate_recommendations(cgpa, internships, projects, all_skills, prediction_result)
        
        return render_template('result.html',
                              resume_text=session.get('resume_text', ''),
                              show_input=True,
                              prediction=prediction_result['prediction'],
                              proba=prediction_result['probability'],
                              cgpa=cgpa,
                              internships=internships,
                              projects=projects,
                              skills=all_skills,
                              charts=charts,
                              recommendations=recommendations)
    
    except Exception as e:
        print(f"Error processing result: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Error processing result: {str(e)}", 'error')
        return redirect(url_for('input_form'))


@app.route('/analyze')
def analyze_page():
    """Render the resume analysis upload page"""
    return render_template('analyze.html')

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('analyze_page'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('analyze_page'))
    
    if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        try:
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Log file processing
            print(f"Processing file: {filename}")
            
            # Extract text from the resume
            text = extract_text_from_resume(filepath)
            print(f"Extracted text length: {len(text)} characters")
            
            # Extract skills for later use
            skills = extract_skills_from_text(text)
            print(f"Extracted skills: {skills}")
            
            # Store in session for use in other pages
            session['resume_text'] = text
            session['resume_skills'] = skills
            
            # Analyze using Mistral AI with config from app
            print(f"Calling Mistral AI API with API key: {app.config['MISTRAL_API_KEY'][:4]}...")
            result = analyze_resume_with_mistral_ai(
                text, 
                api_key=app.config['MISTRAL_API_KEY'],
                api_url=app.config['MISTRAL_API_URL']
            )
            
            # Check if the API call returned an error
            if result.get('error', False):
                error_msg = result.get('message', 'Unknown API error')
                print(f"API Error: {error_msg}")
                flash(f"Analysis failed: {error_msg}", 'error')
                return redirect(url_for('analyze_page'))
            
            print(f"Analysis completed successfully with sections: {list(result.keys())}")
            # Verify the structure of the response
            print(f"ATS Score: {result.get('ats_score')}")
            print(f"Key Info Keys: {list(result.get('key_information', {}).keys())}")
            print(f"Strengths Count: {len(result.get('strengths', []))}")
            
            # Check if we have essential data
            if result.get('ats_score') is None:
                print("Warning: ATS score is missing")
                result['ats_score'] = 60  # Set default score
            
            # Store analysis result in session
            try:
                # Store a simplified version always to avoid session storage issues
                session['analysis_result'] = {
                    "ats_score": result.get("ats_score", 60),
                    "key_information": {
                        "personal_details": result.get("key_information", {}).get("personal_details", []),
                        "education": result.get("key_information", {}).get("education", []),
                        "skills": result.get("key_information", {}).get("skills", []),
                        "experience": result.get("key_information", {}).get("experience", []),
                        "projects": result.get("key_information", {}).get("projects", [])
                    },
                    "strengths": result.get("strengths", [])[:5],
                    "improvements": result.get("improvements", [])[:5],
                    "suitable_roles": result.get("suitable_roles", [])[:5],
                    "skills_to_develop": result.get("skills_to_develop", [])[:5],
                    "recommended_certs": result.get("recommended_certs", [])[:5],
                    "keywords": result.get("keywords", [])[:10],
                }
                print("Analysis result successfully stored in session")
            except Exception as e:
                print(f"Warning: Could not store result in session: {e}")
                # If session storage fails, store minimal data
                session['analysis_result'] = {
                    "ats_score": result.get("ats_score", 60),
                    "error": True,
                    "message": "Session storage error - data too large"
                }
            
            # Redirect to results page
            return redirect(url_for('analysis_result'))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"Error analyzing resume: {str(e)}", 'error')
            print(f"Resume analysis error: {e}")
            return redirect(url_for('analyze_page'))
    else:
        flash(f"Invalid file type. Please upload PDF or DOCX files.", 'error')
        return redirect(url_for('analyze_page'))

@app.route('/analysis_result')
def analysis_result():
    # Get analysis result from session
    result = session.get('analysis_result')
    resume_text = session.get('resume_text', '')
    skills = session.get('resume_skills', [])
    
    print(f"Result keys in analysis_result route: {list(result.keys()) if result else None}")
    
    if not result:
        flash("No analysis result found. Please upload your resume again.", 'error')
        return redirect(url_for('analyze_page'))
    
    # Check if we have an error message
    if result.get('error', False):
        flash(f"Analysis error: {result.get('message', 'Unknown error')}", 'error')
        return redirect(url_for('analyze_page'))
    
    # Check if we have essential data
    if result.get('ats_score') is None:
        result['ats_score'] = 60  # Default score
    
    return render_template(
        'analysis_result.html',
        result=result,
        resume_text=resume_text,
        skills=skills
    )



@app.route('/test-api')
def test_api():
    try:
        # Simple test with minimal content
        result = analyze_resume_with_mistral_ai(
            "Test resume content", 
            api_key=app.config['MISTRAL_API_KEY']
        )
        return f"API test result: {json.dumps(result, indent=2)}"
    except Exception as e:
        return f"API test failed: {str(e)}"


@app.route('/profile')
def profile():
    # For future implementation - User profile view
    return render_template('profile.html')

@app.route('/Dashboard')
def Dashboard():
    # For future implementation - Detailed report view
    return render_template('Dashboard.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)