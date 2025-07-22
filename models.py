from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='teacher')  # 'admin' or 'teacher'
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    users = db.relationship('User', backref='teacher', lazy=True, cascade="all, delete-orphan")
    routines = db.relationship('TeacherRoutine', backref='teacher', lazy=True, cascade="all, delete-orphan")
    absences = db.relationship('Absence', backref='teacher', lazy=True, cascade="all, delete-orphan")
    substitutions = db.relationship('Substitution', backref='substitute_teacher', lazy=True, 
                                    foreign_keys='Substitution.teacher_id', cascade="all, delete-orphan")
    original_substitutions = db.relationship('Substitution', backref='original_teacher', lazy=True, 
                                           foreign_keys='Substitution.original_teacher_id', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Teacher {self.name}>'

class TeacherRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    period = db.Column(db.Integer, nullable=False)  # 1-8
    class_name = db.Column(db.String(20), nullable=False)  # Class name or 'Free'
    section = db.Column(db.String(10), nullable=True)  # A, B, C, etc.
    is_free = db.Column(db.Boolean, default=False)  # If this is a free period
    
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'day', 'period', name='unique_teacher_schedule'),
    )
    
    def __repr__(self):
        return f'<TeacherRoutine {self.teacher.name} {self.day} Period {self.period}>'

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    day = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    reported_by = db.Column(db.String(20), nullable=False, default='admin')  # 'admin' or 'self'
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'date', name='unique_teacher_absence'),
    )
    
    def __repr__(self):
        return f'<Absence {self.teacher.name} on {self.date}>'

class Substitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)  # Substitute teacher
    date = db.Column(db.Date, nullable=False)
    day = db.Column(db.String(10), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Substitution {self.substitute_teacher.name} for {self.original_teacher.name} on {self.date} Period {self.period}>'

class SubstitutionTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    substitution_id = db.Column(db.Integer, db.ForeignKey('substitution.id'), nullable=False)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    new_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    action_date = db.Column(db.DateTime, nullable=True)  # When admin approves/rejects
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    transfer_all = db.Column(db.Boolean, default=False)  # Transfer all substitutions for the day
    
    # Relationships
    substitution = db.relationship('Substitution', backref='transfer_requests')
    original_teacher = db.relationship('Teacher', foreign_keys=[original_teacher_id])
    new_teacher = db.relationship('Teacher', foreign_keys=[new_teacher_id])
    
    def __repr__(self):
        return f'<SubstitutionTransfer from {self.original_teacher.name} to {self.new_teacher.name}, status: {self.status}>'
