from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class ProgramRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProgramRegistration {self.program_name} - {self.full_name}>'

class SessionRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, nullable=False)
    session_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SessionRegistration {self.session_name} - {self.name}>'

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # online/offline
    time = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active/inactive
    category = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Program {self.name}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    program = db.relationship('Program', backref=db.backref('registrations', lazy=True))

    def __repr__(self):
        return f'<Registration User:{self.user_id} Program:{self.program_id}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BlogPost {self.title}>'