
from flask import Blueprint, redirect, url_for, request, flash
from routes import render_template_with_htmx as render_template
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Teacher, db
from forms import LoginForm, AdminForm
from werkzeug.security import check_password_hash, generate_password_hash

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_routes.dashboard'))
        else:
            return redirect(url_for('teacher_routes.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            
            # Redirect to appropriate dashboard
            if user.role == 'admin':
                return redirect(url_for('admin_routes.dashboard'))
            else:
                return redirect(url_for('teacher_routes.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    # Check if any admin exists - only show admin creation option if none exists
    admin_exists = User.query.filter_by(role='admin').first() is not None
    
    return render_template('auth/login.html', form=form, admin_exists=admin_exists)

@auth_routes.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='admin').first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('admin_routes.dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin/login.html', form=form)

@auth_routes.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # First check if a teacher exists with the provided email
        teacher = Teacher.query.filter_by(email=form.email.data).first()
        
        if teacher:
            # Get the first name from the teacher's full name (split by space and take first part)
            first_name = teacher.name.split()[0].lower()
            
            # Check if password matches the teacher's first name (case insensitive)
            if form.password.data.lower() == first_name:
                # Find the associated user account
                user = User.query.filter_by(email=form.email.data, role='teacher').first()
                
                # If no user account exists yet, create one
                if not user:
                    # Create a user account linked to this teacher
                    user = User(
                        username=teacher.email.split('@')[0],  # Use part before @ as username
                        email=teacher.email,
                        password_hash=generate_password_hash(first_name),  # Store hashed version
                        role='teacher',
                        teacher_id=teacher.id
                    )
                    db.session.add(user)
                    db.session.commit()
                
                login_user(user)
                return redirect(url_for('teacher_routes.dashboard'))
        
        # If login fails for any reason, show error
        flash('Invalid teacher credentials. Use your email and first name as password.', 'danger')
    
    return render_template('teacher/login.html', form=form)

@auth_routes.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    # Check if any admin exists
    admin_exists = User.query.filter_by(role='admin').first() is not None
    
    # If admin exists and user is not authenticated as admin, redirect
    if admin_exists and (not current_user.is_authenticated or current_user.role != 'admin'):
        flash('Admin creation is restricted', 'danger')
        return redirect(url_for('auth_routes.login'))
    
    form = AdminForm()
    
    if form.validate_on_submit():
        # Create a new admin user
        new_admin = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role='admin'
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin account created successfully!', 'success')
        
        # If not logged in, redirect to login
        if not current_user.is_authenticated:
            return redirect(url_for('auth_routes.login'))
        # If logged in as admin, redirect to dashboard
        else:
            return redirect(url_for('admin_routes.dashboard'))
    
    return render_template('auth/create_admin.html', form=form, admin_exists=admin_exists)

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth_routes.login'))
