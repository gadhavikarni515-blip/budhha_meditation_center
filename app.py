from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nirvana_buddha.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', '')

db = SQLAlchemy(app)
mail = Mail(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'programs'), exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'online' or 'offline'
    time = db.Column(db.String(50), nullable=False)  # Keep for backward compatibility
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    photo = db.Column(db.String(255))
    category = db.Column(db.String(100))  # Child, Pregnant Women, Relaxation, Inner Journey
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='registrations')
    program = db.relationship('Program', backref='registrations')

class ProgramRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SessionRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('program.id'))
    session_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    author = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    sessions = Program.query.filter_by(status='active').order_by(Program.date.desc()).all()
    return render_template('index.html', sessions=sessions)

@app.route('/programs')
def programs():
    all_programs = Program.query.filter_by(status='active').order_by(Program.date.desc()).all()
    return render_template('programs.html', programs=all_programs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        contact_entry = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(contact_entry)
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                subject=f'New Contact Form Submission from {name}',
                recipients=[app.config['MAIL_USERNAME']],
                body=f'''
Name: {name}
Email: {email}
Phone: {phone}
Message: {message}
                '''
            )
            mail.send(msg)
        except:
            pass
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/register_program_modal', methods=['POST'])
def register_program_modal():
    """Handle program registration from modal - simple registration without user account"""
    program_name = request.form.get('program_name')
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    
    if not all([program_name, full_name, phone]):
        return jsonify({'error': 'Program name, full name, and phone are required'}), 400
    
    # Create program registration record
    program_registration = ProgramRegistration(
        program_name=program_name,
        full_name=full_name,
        phone=phone,
        email=email if email else None
    )
    db.session.add(program_registration)
    db.session.commit()
    
    # Send confirmation email if email provided
    if email:
        try:
            confirmation_message = f'''
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #8b6bb6; margin-bottom: 20px;">🙏 Registration Confirmed!</h2>
                        <p>Thank you for registering for our program!</p>
                        
                        <div style="background-color: #f0e6f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #8b6bb6; margin-top: 0;">Program Details:</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><strong>Program:</strong> {program_name}</li>
                            </ul>
                        </div>
                        
                        <p style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <strong>Note:</strong> We'll send you program details and schedule information soon.
                        </p>
                        
                        <p>We look forward to seeing you at our meditation center!</p>
                        
                        <div style="border-top: 1px solid #ddd; margin-top: 20px; padding-top: 20px;">
                            <p style="font-size: 14px; color: #666;">Best regards,<br><strong>Nirvana Buddha Meditation Center</strong></p>
                            <p style="font-size: 12px; color: #999;">📞 +91 98256 32306</p>
                        </div>
                    </div>
                </body>
            </html>
            '''
            
            msg = Message(
                subject='Program Registration Confirmed - Nirvana Buddha Meditation Center',
                recipients=[email],
                html=confirmation_message
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email send error: {str(e)}")
            pass
    
    return jsonify({'message': 'Registration successful! Confirmation email has been sent to your email address.'}), 200

@app.route('/register_session_modal', methods=['POST'])
def register_session_modal():
    """Handle session registration from modal"""
    session_id = request.form.get('session_id')
    session_name = request.form.get('session_name')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    if not all([session_id, session_name, name, email, phone]):
        return jsonify({'error': 'All fields are required'}), 400
    
    # Create session registration record
    session_registration = SessionRegistration(
        session_id=int(session_id),
        session_name=session_name,
        name=name,
        email=email,
        phone=phone
    )
    db.session.add(session_registration)
    db.session.commit()
    
    # Send confirmation email
    try:
        # Get session details if available
        session_obj = Program.query.get(int(session_id))
        session_time = f"{session_obj.start_time} - {session_obj.end_time}" if session_obj and session_obj.start_time and session_obj.end_time else "See schedule"
        
        confirmation_message = f'''
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #8b6bb6; margin-bottom: 20px;">🙏 Session Registration Confirmed!</h2>
                    <p>Hi <strong>{name}</strong>,</p>
                    <p>Thank you for registering for our session!</p>
                    
                    <div style="background-color: #f0e6f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #8b6bb6; margin-top: 0;">Session Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Session:</strong> {session_name}</li>
                            <li><strong>Time:</strong> {session_time}</li>
                        </ul>
                    </div>
                    
                    <p style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <strong>Note:</strong> Please arrive 10 minutes early. Bring your yoga mat and water bottle.
                    </p>
                    
                    <p>We look forward to seeing you at our meditation center!</p>
                    
                    <div style="border-top: 1px solid #ddd; margin-top: 20px; padding-top: 20px;">
                        <p style="font-size: 14px; color: #666;">Best regards,<br><strong>Nirvana Buddha Meditation Center</strong></p>
                        <p style="font-size: 12px; color: #999;">📞 +91 98256 32306</p>
                    </div>
                </div>
            </body>
        </html>
        '''
        
        msg = Message(
            subject='Session Registration Confirmed - Nirvana Buddha Meditation Center',
            recipients=[email],
            html=confirmation_message
        )
        mail.send(msg)
    except Exception as e:
        print(f"Email send error: {str(e)}")
        pass
    
    return jsonify({'message': 'Session registration successful! Confirmation email has been sent.'}), 200

@app.route('/register/<int:program_id>', methods=['POST'])
def register_program(program_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    program = Program.query.get_or_404(program_id)
    
    # Check if already registered
    existing = Registration.query.filter_by(user_id=session['user_id'], program_id=program_id).first()
    if existing:
        return jsonify({'error': 'Already registered for this program'}), 400
    
    registration = Registration(user_id=session['user_id'], program_id=program_id)
    db.session.add(registration)
    db.session.commit()
    
    # Send confirmation email
    user = User.query.get(session['user_id'])
    try:
        msg = Message(
            subject='Registration Confirmation - Nirvana Buddha Meditation Center',
            recipients=[user.email],
            html=f'''
            <h2>Registration Confirmed!</h2>
            <p>Dear {user.name},</p>
            <p>Thank you for registering for our program: <strong>{program.name}</strong></p>
            <p><strong>Program Details:</strong></p>
            <ul>
                <li>Date: {program.date}</li>
                <li>Time: {program.start_time.strftime('%I:%M %p') + ' - ' + program.end_time.strftime('%I:%M %p') if program.start_time and program.end_time else program.time}</li>
                <li>Type: {program.type.title()}</li>
            </ul>
            <p>We look forward to seeing you!</p>
            <p>Best regards,<br>Nirvana Buddha Meditation Center</p>
            '''
        )
        mail.send(msg)
    except:
        pass
    
    return jsonify({'message': 'Registration successful! Confirmation email sent.'}), 200

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and check_password_hash(user.password_hash, password):
            session['admin_id'] = user.id
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    programs = Program.query.order_by(Program.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
    registrations = Registration.query.order_by(Registration.created_at.desc()).limit(10).all()
    program_registrations = ProgramRegistration.query.order_by(ProgramRegistration.created_at.desc()).limit(10).all()
    session_registrations = SessionRegistration.query.order_by(SessionRegistration.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         programs=programs, 
                         users=users, 
                         contacts=contacts,
                         registrations=registrations,
                         program_registrations=program_registrations,
                         session_registrations=session_registrations)

@app.route('/admin/programs', methods=['GET', 'POST'])
def admin_programs():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        time_str = request.form.get('time', '')
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        description = request.form.get('description')
        status = request.form.get('status', 'active')
        category = request.form.get('category')
        
        # Parse start_time and end_time
        start_time = None
        end_time = None
        if start_time_str:
            try:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
            except:
                pass
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except:
                pass
        
        # If time pickers are used, format time string
        if start_time and end_time:
            time_str = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        elif not time_str and start_time:
            time_str = start_time.strftime('%I:%M %p')
        
        photo = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'programs', filename)
                file.save(filepath)
                photo = f'uploads/programs/{filename}'
        
        program = Program(
            name=name, type=type, time=time_str, date=date,
            description=description, status=status, category=category, photo=photo,
            start_time=start_time, end_time=end_time
        )
        db.session.add(program)
        db.session.commit()
        flash('Program created successfully!', 'success')
        return redirect(url_for('admin_programs'))
    
    programs = Program.query.order_by(Program.created_at.desc()).all()
    return render_template('admin/programs.html', programs=programs)

@app.route('/admin/programs/<int:id>/edit', methods=['GET', 'POST'])
def admin_edit_program(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    program = Program.query.get_or_404(id)
    
    if request.method == 'POST':
        program.name = request.form.get('name')
        program.type = request.form.get('type')
        time_str = request.form.get('time', '')
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        program.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        program.description = request.form.get('description')
        program.status = request.form.get('status', 'active')
        program.category = request.form.get('category')
        
        # Parse start_time and end_time
        start_time = None
        end_time = None
        if start_time_str:
            try:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
            except:
                pass
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except:
                pass
        
        # If time pickers are used, format time string
        if start_time and end_time:
            time_str = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        elif not time_str and start_time:
            time_str = start_time.strftime('%I:%M %p')
        
        program.time = time_str
        program.start_time = start_time
        program.end_time = end_time
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'programs', filename)
                file.save(filepath)
                program.photo = f'uploads/programs/{filename}'
        
        db.session.commit()
        flash('Program updated successfully!', 'success')
        return redirect(url_for('admin_programs'))
    
    return render_template('admin/edit_program.html', program=program)

@app.route('/admin/programs/<int:id>/delete', methods=['POST'])
def admin_delete_program(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    program = Program.query.get_or_404(id)
    db.session.delete(program)
    db.session.commit()
    flash('Program deleted successfully!', 'success')
    return redirect(url_for('admin_programs'))

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/program-registrations')
def admin_program_registrations():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    # Get all program registrations grouped by program name
    all_registrations = ProgramRegistration.query.order_by(ProgramRegistration.created_at.desc()).all()
    
    # Group by program name
    registrations_by_program = {}
    for reg in all_registrations:
        if reg.program_name not in registrations_by_program:
            registrations_by_program[reg.program_name] = []
        registrations_by_program[reg.program_name].append(reg)
    
    return render_template('admin/program_registrations.html', 
                         registrations_by_program=registrations_by_program,
                         all_registrations=all_registrations)

@app.route('/admin/session-registrations')
def admin_session_registrations():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    # Get all session registrations grouped by session name
    all_registrations = SessionRegistration.query.order_by(SessionRegistration.created_at.desc()).all()
    
    # Group by session name
    registrations_by_session = {}
    for reg in all_registrations:
        if reg.session_name not in registrations_by_session:
            registrations_by_session[reg.session_name] = []
        registrations_by_session[reg.session_name].append(reg)
    
    return render_template('admin/session_registrations.html', 
                         registrations_by_session=registrations_by_session,
                         all_registrations=all_registrations)

# User registration/login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                name='Admin',
                email='admin@nirvanabuddha.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)

