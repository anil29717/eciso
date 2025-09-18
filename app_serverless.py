from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import random
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Use /tmp for serverless

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory data storage (replace database)
questions_data = [
    {
        "id": 1,
        "category": "Technology",
        "question_text": "What is the primary purpose of a firewall in cybersecurity?",
        "option_a": "To speed up internet connection",
        "option_b": "To block unauthorized access",
        "option_c": "To store passwords",
        "option_d": "To backup data",
        "correct_answer": "B"
    },
    {
        "id": 2,
        "category": "Finance",
        "question_text": "Which regulation requires financial institutions to protect customer data?",
        "option_a": "GDPR",
        "option_b": "SOX",
        "option_c": "PCI DSS",
        "option_d": "GLBA",
        "correct_answer": "D"
    },
    {
        "id": 3,
        "category": "Healthcare",
        "question_text": "What does HIPAA primarily protect?",
        "option_a": "Financial records",
        "option_b": "Patient health information",
        "option_c": "Employee data",
        "option_d": "Marketing data",
        "correct_answer": "B"
    }
]

industries_data = [
    {"name": "Technology", "is_highlighted": True},
    {"name": "Healthcare", "is_highlighted": True},
    {"name": "Finance", "is_highlighted": True},
    {"name": "Manufacturing", "is_highlighted": True},
    {"name": "Retail", "is_highlighted": True},
    {"name": "Education", "is_highlighted": True},
    {"name": "Government", "is_highlighted": True},
    {"name": "Energy", "is_highlighted": True},
    {"name": "Other", "is_highlighted": False}
]

# In-memory storage for game sessions
game_sessions = []
user_journeys = []

@app.route('/')
def welcome():
    return render_template('game/welcome.html')

@app.route('/user-info')
def user_info():
    return render_template('game/user_info.html')

@app.route('/submit-user-info', methods=['POST'])
def submit_user_info():
    data = request.get_json()
    
    # Store user info in session
    session['user_name'] = data.get('name')
    session['company_name'] = data.get('company_name')
    session['email'] = data.get('email', '')
    session['phone'] = data.get('phone', '')
    session['job_title'] = data.get('job_title', '')
    session['department'] = data.get('department', '')
    session['journey_id'] = str(uuid.uuid4())
    
    return jsonify({'success': True})

@app.route('/industry-select')
def industry_select():
    highlighted_industries = [industry for industry in industries_data if industry['is_highlighted']]
    other_industries = [industry for industry in industries_data if not industry['is_highlighted']]
    return render_template('game/industry_select.html', 
                         highlighted_industries=highlighted_industries,
                         other_industries=other_industries)

@app.route('/company-info')
def company_info():
    return render_template('game/company_info.html')

@app.route('/submit-company-info', methods=['POST'])
def submit_company_info():
    data = request.get_json()
    session['industry'] = data.get('industry')
    return jsonify({'success': True})

@app.route('/question')
def question():
    industry = session.get('industry', 'Technology')
    
    # Filter questions by industry or get random question
    industry_questions = [q for q in questions_data if q['category'] == industry]
    if not industry_questions:
        industry_questions = questions_data
    
    question = random.choice(industry_questions)
    session['current_question_id'] = question['id']
    
    return render_template('game/question.html', question=question)

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    selected_answer = data.get('answer')
    question_id = session.get('current_question_id')
    
    # Find the question
    question = next((q for q in questions_data if q['id'] == question_id), None)
    if not question:
        return jsonify({'success': False, 'error': 'Question not found'})
    
    is_correct = selected_answer.upper() == question['correct_answer'].upper()
    
    # Store game session data
    game_session = {
        'id': len(game_sessions) + 1,
        'journey_id': session.get('journey_id'),
        'name': session.get('user_name'),
        'company_name': session.get('company_name'),
        'industry': session.get('industry'),
        'question_id': question_id,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'timestamp': datetime.now().isoformat()
    }
    game_sessions.append(game_session)
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': question['correct_answer']
    })

@app.route('/selfie-capture')
def selfie_capture():
    return render_template('game/selfie_capture.html')

@app.route('/upload-selfie', methods=['POST'])
def upload_selfie():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if image_data:
            # For serverless, we'll just acknowledge the upload
            # In production, you'd upload to cloud storage
            session['selfie_uploaded'] = True
            return jsonify({'success': True, 'message': 'Selfie uploaded successfully'})
        
        return jsonify({'success': False, 'error': 'No image data received'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/feedback')
def feedback():
    return render_template('game/feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    # Store feedback (in production, save to cloud storage or send email)
    return jsonify({'success': True})

@app.route('/thank-you')
def thank_you():
    # Mark journey as completed
    journey = {
        'id': len(user_journeys) + 1,
        'journey_id': session.get('journey_id'),
        'name': session.get('user_name'),
        'company_name': session.get('company_name'),
        'industry': session.get('industry'),
        'completed_at': datetime.now().isoformat(),
        'is_completed': True
    }
    user_journeys.append(journey)
    
    return render_template('game/thank_you.html')

# Admin routes (simplified)
@app.route('/admin')
def admin_dashboard():
    stats = {
        'total_sessions': len(game_sessions),
        'completed_journeys': len(user_journeys),
        'total_questions': len(questions_data)
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/analytics')
def admin_analytics():
    return render_template('admin/analytics.html', 
                         sessions=game_sessions, 
                         journeys=user_journeys)

# API Routes
@app.route('/api/get-suggestions', methods=['POST'])
@cross_origin()
def get_suggestions():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'suggestions': []})
            
        query = data.get('query', '').strip().lower()
        suggestion_type = data.get('type', 'name')
        
        if not query or len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = []
        
        if suggestion_type == 'name':
            # Sample names for suggestions
            sample_names = [
                'John Smith', 'Jane Doe', 'Michael Johnson', 'Sarah Wilson',
                'David Brown', 'Lisa Davis', 'Robert Miller', 'Jennifer Garcia',
                'William Rodriguez', 'Mary Martinez', 'James Anderson', 'Patricia Taylor'
            ]
            matching_names = [name for name in sample_names if query in name.lower()]
            suggestions = matching_names[:10]
        
        elif suggestion_type == 'company':
            # Sample companies for suggestions
            sample_companies = [
                'Microsoft Corporation', 'Apple Inc.', 'Google LLC', 'Amazon.com Inc.',
                'Meta Platforms Inc.', 'Tesla Inc.', 'Netflix Inc.', 'Adobe Inc.',
                'Salesforce Inc.', 'Oracle Corporation', 'IBM Corporation', 'Intel Corporation'
            ]
            matching_companies = [company for company in sample_companies if query in company.lower()]
            suggestions = matching_companies[:10]
        
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return jsonify({'error': str(e), 'suggestions': []}), 500

@app.route('/api/start-game', methods=['POST'])
@cross_origin()
def start_game():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Get user information from request
        name = data.get('name')
        company_name = data.get('company_name')
        industry = data.get('industry')
        email = data.get('email', '')
        phone = data.get('phone', '')
        job_title = data.get('job_title', '')
        department = data.get('department', '')
        
        # Check if this is an industry update for existing session
        if industry and not name and not company_name and 'journey_id' in session:
            session['industry'] = industry
            return jsonify({'success': True, 'message': 'Industry updated'})
        
        # Create new game session
        if name and company_name:
            journey_id = str(uuid.uuid4())
            session['journey_id'] = journey_id
            session['name'] = name
            session['company_name'] = company_name
            session['industry'] = industry
            session['email'] = email
            session['phone'] = phone
            session['job_title'] = job_title
            session['department'] = department
            session['current_question'] = 0
            session['score'] = 0
            session['start_time'] = datetime.now().isoformat()
            
            # Store in memory
            user_journeys.append({
                'id': journey_id,
                'name': name,
                'company_name': company_name,
                'industry': industry,
                'email': email,
                'phone': phone,
                'job_title': job_title,
                'department': department,
                'start_time': datetime.now().isoformat(),
                'completed': False
            })
            
            return jsonify({'success': True, 'message': 'Game started successfully'})
        
        return jsonify({'success': False, 'message': 'Missing required information'})
    
    except Exception as e:
        print(f"Error starting game: {e}")
        return jsonify({'success': False, 'error': str(e), 'message': 'Server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)