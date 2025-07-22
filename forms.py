from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from models import Teacher, User
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=64)])
    teacher_id = StringField('Teacher ID', validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Teacher')
    
    def validate_teacher_id(self, field):
        teacher = Teacher.query.filter_by(teacher_id=field.data).first()
        if teacher and teacher.id != getattr(self, '_teacher_id', None):
            raise ValidationError('This Teacher ID is already in use.')
    
    def validate_email(self, field):
        teacher = Teacher.query.filter_by(email=field.data).first()
        if teacher and teacher.id != getattr(self, '_teacher_id', None):
            raise ValidationError('This email address is already in use.')

class AbsenceForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], default=datetime.now)
    day = SelectField('Day', choices=[
        ('Day 1', 'Day 1'),
        ('Day 2', 'Day 2'),
        ('Day 3', 'Day 3'),
        ('Day 4', 'Day 4'),
        ('Day 5', 'Day 5')
    ], validators=[DataRequired()])
    # We don't include selected_teachers here but handle it manually in the route
    # because we need to process multiple checkbox values
    submit = SubmitField('Mark Absences')

class TransferRequestForm(FlaskForm):
    substitution_id = HiddenField('Substitution ID', validators=[DataRequired()])
    reason = StringField('Reason', validators=[DataRequired(), Length(min=5)])
    new_teacher_id = SelectField('New Teacher', coerce=int, validators=[DataRequired()])
    transfer_all = SelectField('Transfer Type', choices=[
        ('single', 'Transfer only this period'),
        ('all', 'Transfer all my substitutions for today')
    ], default='single')
    submit = SubmitField('Request Transfer')
    
class AdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Create Admin')
    
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('This email address is already in use.')