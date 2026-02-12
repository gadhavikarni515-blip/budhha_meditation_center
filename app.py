from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, time
import os
from dotenv import load_dotenv
from models import db, User, Program, Contact, Registration, ProgramRegistration, SessionRegistration, BlogPost

load_dotenv()

app = Flask(__name__)

# Production-ready configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.getenv('SECRET_KEY', 'dev-secret-key'))
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', os.getenv('MAIL_SERVER', 'smtp.gmail.com'))
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', os.getenv('MAIL_PORT', 587)))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', os.getenv('MAIL_USERNAME', ''))
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', os.getenv('MAIL_PASSWORD', ''))
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', os.getenv('MAIL_USERNAME', ''))

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'programs'), exist_ok=True)


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
        except Exception as e:
            print(f"Email send error: {str(e)}")
            pass
        
        # Check if AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.'
            })
        else:
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml"""
    from urllib.parse import urljoin
    base_url = request.url_root.rstrip('/')
    pages = [
        {'loc': url_for('index', _external=True), 'lastmod': '2024-01-01', 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': url_for('about', _external=True), 'lastmod': '2024-01-01', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': url_for('programs', _external=True), 'lastmod': '2024-01-01', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': url_for('contact', _external=True), 'lastmod': '2024-01-01', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': url_for('blog', _external=True), 'lastmod': '2024-01-01', 'changefreq': 'weekly', 'priority': '0.6'},
    ]

    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    for page in pages:
        sitemap_xml += f'''  <url>
    <loc>{page['loc']}</loc>
    <lastmod>{page['lastmod']}</lastmod>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
  </url>
'''
    sitemap_xml += '</urlset>'
    return sitemap_xml, 200, {'Content-Type': 'application/xml'}

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    robots_txt = f'''User-agent: *
Allow: /

Sitemap: {url_for('sitemap', _external=True)}
'''
    return robots_txt, 200, {'Content-Type': 'text/plain'}

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
        
        # Handle image upload as BLOB
        photo_data = None
        photo_filename = None
        photo_mime_type = None
        photo = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                # Read file as BLOB
                photo_data = file.read()
                photo_filename = secure_filename(file.filename)
                photo_mime_type = file.content_type or 'image/jpeg'
        
        program = Program(
            name=name, type=type, time=time_str, date=date,
            description=description, status=status, category=category, photo=photo,
            photo_data=photo_data,
            photo_filename=photo_filename,
            photo_mime_type=photo_mime_type,
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
        
        # Handle image upload as BLOB
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                # Read file as BLOB
                program.photo_data = file.read()
                program.photo_filename = secure_filename(file.filename)
                program.photo_mime_type = file.content_type or 'image/jpeg'
                program.photo = None  # Clear old file-based path
        
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

@app.route('/admin/contacts')
def admin_contacts():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    search_query = request.args.get('search', '')
    if search_query:
        contacts = Contact.query.filter(
            (Contact.name.contains(search_query)) | 
            (Contact.email.contains(search_query)) |
            (Contact.message.contains(search_query))
        ).order_by(Contact.created_at.desc()).all()
    else:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/contacts/<int:id>/reply', methods=['POST'])
def admin_reply_contact(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    contact = Contact.query.get_or_404(id)
    
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    try:
        msg = Message(
            subject=subject,
            recipients=[email],
            body=message
        )
        mail.send(msg)
        flash(f'Reply sent to {email}', 'success')
    except Exception as e:
        flash(f'Failed to send reply: {str(e)}', 'error')
    
    return redirect(url_for('admin_contacts'))

@app.route('/admin/contacts/<int:id>/delete', methods=['POST'])
def admin_delete_contact(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact message deleted successfully!', 'success')
    return redirect(url_for('admin_contacts'))

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

# Image serving route for BLOB images
@app.route('/program-image/<int:program_id>')
def serve_program_image(program_id):
    """Serve program image from database BLOB"""
    program = Program.query.get_or_404(program_id)
    
    if program.photo_data:
        # Return the BLOB data with MIME type
        return program.photo_data, 200, {
            'Content-Type': program.photo_mime_type or 'image/jpeg',
            'Cache-Control': 'max-age=3600'  # Cache for 1 hour
        }
    
    # Fallback to file-based image if BLOB doesn't exist
    if program.photo:
        from flask import send_from_directory
        import os
        upload_folder = app.config['UPLOAD_FOLDER']
        photo_path = os.path.join(upload_folder, program.photo)
        if os.path.exists(photo_path):
            return send_from_directory(upload_folder, program.photo)
    
    # Return default image
    from flask import send_from_directory
    return send_from_directory('static/images', 'logo.png')

# Production initialization
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

def create_admin_user():
    """Create default admin user if not exists"""
    with app.app_context():
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                name='Admin',
                email='admin@nirvanabuddha.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")

if __name__ == '__main__':
    create_tables()
    create_admin_user()
    app.run(debug=True)
else:
    # Production mode - ensure tables exist
    create_tables()
    create_admin_user()

