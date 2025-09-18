from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import random
import openpyxl
from openpyxl.styles import Font, Alignment
import io
import base64
from PIL import Image
from dotenv import load_dotenv
from config import get_config

# Load environment variables
load_dotenv()

app = Flask(__name__)
config_class = get_config()
app.config.from_object(config_class)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Use the database path from environment or default to instance directory
db_path = os.path.join(os.getcwd(), 'instance', 'game_database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Database Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='category', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Industry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_highlighted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PreRegisteredUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    session_id = db.Column(db.String(100), unique=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    game_sessions = db.relationship('GameSession', backref='user', lazy=True, foreign_keys='GameSession.user_id')

class UserJourney(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    journey_session_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique identifier for complete journey
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    selfie_filename = db.Column(db.String(200))
    journey_start = db.Column(db.DateTime, default=datetime.utcnow)
    journey_end = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)  # True when user reaches gift collection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='user_journeys')
    game_sessions = db.relationship('GameSession', backref='user_journey', lazy=True)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('user_journey.id'), nullable=True)  # Link to complete journey
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    selfie_filename = db.Column(db.String(200))
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.relationship('Question', backref='game_sessions')

# Import routes after app initialization
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        if not Admin.query.filter_by(username=admin_username).first():
            admin = Admin(
                username=admin_username,
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: username='{admin_username}'")
        
        # Create default industries if not exist
        default_industries = [
            ('Technology', True), ('Healthcare', True), ('Finance', True), 
            ('Manufacturing', True), ('Retail', True), ('Education', True),
            ('Government', True), ('Energy', True), ('Telecommunications', False),
            ('Transportation', False), ('Real Estate', False), ('Media', False),
            ('Hospitality', False), ('Agriculture', False), ('Construction', False),
            ('Automotive', False), ('Aerospace', False), ('Pharmaceuticals', False),
            ('Insurance', False), ('Banking', False), ('Consulting', False),
            ('Legal Services', False), ('Non-Profit', False), ('Other', False)
        ]
        
        for industry_name, is_highlighted in default_industries:
            if not Industry.query.filter_by(name=industry_name).first():
                industry = Industry(name=industry_name, is_highlighted=is_highlighted)
                db.session.add(industry)
        
        # Create default categories matching industries
        for industry_name, _ in default_industries:
            if not Category.query.filter_by(name=industry_name).first():
                category = Category(name=industry_name)
                db.session.add(category)
        
        db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)