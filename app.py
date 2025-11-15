"""
EduMentor AI - Main Flask Application
A comprehensive AI-powered e-learning platform that generates
learning materials, quizzes, flashcards, and more.
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
from modules.ai_generator import AIGenerator
from modules.export_manager import ExportManager
from modules.progress_tracker import ProgressTracker
from modules.quiz_fetcher import QuizFetcher
from modules.study_material_fetcher import StudyMaterialFetcher

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edumentor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Initialize custom modules (ProgressTracker will be initialized after Progress model is defined)
ai_generator = AIGenerator()
export_manager = ExportManager()
# Initialize quiz fetcher with AI generator as fallback
quiz_fetcher = QuizFetcher(ai_generator=ai_generator)
# Initialize study material fetcher with AI generator for compiling internet content
study_material_fetcher = StudyMaterialFetcher(ai_generator=ai_generator)

# Database Models
class User(db.Model):
    """User model for storing user information and progress"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # student, teacher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('Progress', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)

class Progress(db.Model):
    """Progress tracking model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    difficulty_level = db.Column(db.String(20), default='medium')
    score = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text)  # JSON data for additional progress info

class GeneratedContent(db.Model):
    """Store generated content for later retrieval"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Track who generated it
    content_type = db.Column(db.String(50), nullable=False)  # notes, quiz, flashcard, etc.
    topic = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content_metadata = db.Column(db.Text)  # JSON metadata

# Initialize ProgressTracker after Progress model is defined
progress_tracker = ProgressTracker(db, Progress)

# Authentication Decorators
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user and user.role not in roles:
                    if request.is_json:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                    flash('You do not have permission to access this page', 'danger')
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Username and password are required'}), 400
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role
                    }
                })
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
    
    # If already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'student').strip().lower()  # Default to student
        
        # Validate role
        if role not in ['student', 'teacher', 'admin']:
            role = 'student'
        
        # Only allow admin to create admin accounts
        if role == 'admin' and session.get('role') != 'admin':
            role = 'student'
        
        # Validation
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'error': 'All fields are required'}), 400
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            if request.is_json:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'error': 'Username already exists'}), 400
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already exists'}), 400
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Auto-login after registration
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role
                    }
                })
            flash('Registration successful! Welcome!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash('An error occurred during registration', 'danger')
            return render_template('register.html')
    
    # If already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Routes
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/quiz')
@login_required
def quiz_page():
    """Quiz generation page - requires login"""
    return render_template('quiz.html')

@app.route('/flashcards')
@login_required
def flashcards_page():
    """Flashcards generation page - requires login"""
    return render_template('flashcards.html')

@app.route('/doubt-solver')
@login_required
def doubt_solver_page():
    """Doubt solver page - requires login"""
    return render_template('doubt-solver.html')

@app.route('/lesson-plan')
@role_required('teacher', 'admin')
def lesson_plan_page():
    """Lesson plan generation page - requires teacher or admin role"""
    return render_template('lesson-plan.html')

@app.route('/homework')
@role_required('teacher', 'admin')
def homework_page():
    """Homework generation page - requires teacher or admin role"""
    return render_template('homework.html')

@app.route('/progress')
@login_required
def progress_page():
    """Progress tracking page - requires login"""
    return render_template('progress.html')

@app.route('/generate', methods=['POST'])
@login_required
def generate_content():
    """Generate learning content based on topic and content type - requires login"""
    try:
        user_id = session.get('user_id')
        data = request.json
        topic = data.get('topic', '')
        content_type = data.get('content_type', 'notes')  # notes, summary, quiz, etc.
        difficulty = data.get('difficulty', 'medium')
        language = data.get('language', 'en')
        use_internet = data.get('use_internet', False)  # Option to generate from internet
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Handle quiz generation specially - use dedicated quiz generation
        if content_type == 'quiz':
            # Validate topic is not empty (already checked above, but ensure it's clean)
            topic = topic.strip()
            if not topic:
                return jsonify({'error': 'Topic is required for quiz generation'}), 400
            
            # Generate quiz questions directly using AI for the given topic
            # The topic entered by the user is passed to generate topic-specific questions
            num_questions = data.get('num_questions', 10)  # Default to 10 questions
            
            # Generate quiz questions based on the user's topic
            quiz_result = ai_generator.generate_quiz(
                topic=topic,  # User's entered topic - used to generate relevant questions
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            # Format quiz result to match expected structure
            # Include the topic in the result so frontend can display it
            result = {
                'type': 'quiz',
                'topic': topic,  # Store the topic for reference
                'questions': quiz_result.get('questions', []),
                'difficulty': difficulty
            }
        # Generate content - use internet sources if requested
        elif use_internet:
            # Fetch from internet and compile using AI
            result = study_material_fetcher.compile_study_material(
                topic=topic,
                content_type=content_type,
                difficulty=difficulty,
                language=language
            )
        else:
            # Generate content using AI only
            result = ai_generator.generate(
                topic=topic,
                content_type=content_type,
                difficulty=difficulty,
                language=language
            )
        
        # Save to database
        content = GeneratedContent(
            user_id=user_id,
            content_type=content_type,
            topic=topic,
            content=json.dumps(result),
            content_metadata=json.dumps({
                'difficulty': difficulty, 
                'language': language,
                'use_internet': use_internet
            })
        )
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'content': result,
            'content_id': content.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quiz', methods=['POST'])
@login_required
def generate_quiz():
    """Generate quiz with questions and answers from internet sources - requires login"""
    try:
        data = request.json
        topic = data.get('topic', '')
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Fetch quiz from internet sources (with AI fallback)
        quiz = quiz_fetcher.fetch_quiz(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        return jsonify({'success': True, 'quiz': quiz})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-quiz-questions', methods=['POST'])
@login_required
def generate_quiz_questions():
    """
    Generate quiz questions directly using AI for a given topic
    This endpoint focuses on generating questions based on user-provided topics
    """
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        # Validate topic is provided
        if not topic:
            return jsonify({'error': 'Topic is required. Please provide a topic for quiz generation.'}), 400
        
        # Validate number of questions
        try:
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 50:
                return jsonify({'error': 'Number of questions must be between 1 and 50'}), 400
        except (ValueError, TypeError):
            num_questions = 10
        
        # Validate difficulty
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'medium'
        
        # Generate quiz questions directly using AI
        # This ensures we always get questions related to the specific topic
        quiz = ai_generator.generate_quiz(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        # Validate that we got questions
        if not quiz or not quiz.get('questions'):
            return jsonify({
                'error': 'Failed to generate quiz questions. Please try again or check your API configuration.'
            }), 500
        
        # Return the generated quiz questions
        return jsonify({
            'success': True,
            'topic': topic,
            'num_questions': len(quiz.get('questions', [])),
            'difficulty': difficulty,
            'quiz': quiz
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating quiz questions: {str(e)}'}), 500

@app.route('/flashcards', methods=['POST'])
@login_required
def generate_flashcards():
    """Generate flashcards for a topic - requires login"""
    try:
        data = request.json
        topic = data.get('topic', '')
        num_cards = data.get('num_cards', 20)
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        flashcards = ai_generator.generate_flashcards(
            topic=topic,
            num_cards=num_cards
        )
        
        return jsonify({'success': True, 'flashcards': flashcards})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/doubt-solve', methods=['POST'])
@login_required
def solve_doubt():
    """AI-powered doubt solving - requires login"""
    try:
        data = request.json
        question = data.get('question', '')
        context = data.get('context', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        answer = ai_generator.solve_doubt(question, context)
        
        return jsonify({'success': True, 'answer': answer})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export', methods=['POST'])
@login_required
def export_content():
    """Export content in various formats (PDF, PPT, DOCX) - requires login"""
    try:
        data = request.json
        content_id = data.get('content_id')
        export_format = data.get('format', 'pdf')  # pdf, ppt, docx
        content_data = data.get('content')
        
        if not content_data and not content_id:
            return jsonify({'error': 'Content is required'}), 400
        
        # Get content if ID provided
        if content_id:
            content = GeneratedContent.query.get(content_id)
            if not content:
                return jsonify({'error': 'Content not found'}), 404
            content_data = json.loads(content.content)
        
        # Export based on format
        file_path = export_manager.export(
            content=content_data,
            format_type=export_format,
            filename=f"edumentor_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"edumentor_export.{export_format}"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress', methods=['GET', 'POST'])
@login_required
def handle_progress():
    """Get or update user progress - requires login"""
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        # Get progress for logged-in user
        progress = progress_tracker.get_progress(user_id=user_id)
        return jsonify({'success': True, 'progress': progress})
    
    else:  # POST
        data = request.json
        topic = data.get('topic')
        score = data.get('score', 0)
        difficulty = data.get('difficulty', 'medium')
        
        progress_tracker.update_progress(
            topic=topic,
            score=score,
            difficulty=difficulty,
            user_id=user_id
        )
        
        return jsonify({'success': True})

@app.route('/lesson-plan', methods=['POST'])
@role_required('teacher', 'admin')
def generate_lesson_plan():
    """Generate lesson plan for teachers - requires teacher or admin role"""
    try:
        data = request.json
        topic = data.get('topic', '')
        duration = data.get('duration', 60)  # minutes
        grade_level = data.get('grade_level', 'middle')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        lesson_plan = ai_generator.generate_lesson_plan(
            topic=topic,
            duration=duration,
            grade_level=grade_level
        )
        
        return jsonify({'success': True, 'lesson_plan': lesson_plan})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/homework', methods=['POST'])
@role_required('teacher', 'admin')
def generate_homework():
    """Generate homework assignments - requires teacher or admin role"""
    try:
        data = request.json
        topic = data.get('topic', '')
        difficulty = data.get('difficulty', 'medium')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        homework = ai_generator.generate_homework(
            topic=topic,
            difficulty=difficulty
        )
        
        return jsonify({'success': True, 'homework': homework})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
def create_tables():
    """Create database tables and create default admin user"""
    with app.app_context():
        # Drop all existing tables and recreate them
        # This ensures the schema is always up to date in development
        # WARNING: This will delete all existing data!
        db.drop_all()
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@edumentor.ai',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")

if __name__ == '__main__':
    # Create database tables on startup
    create_tables()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

