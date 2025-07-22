import os
import logging
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "temporary-dev-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database from environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///school.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = True

# Initialize the extensions
db.init_app(app)
csrf.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_routes.login'

with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from models import User, Teacher, TeacherRoutine, Absence, Substitution, SubstitutionTransfer
    
    # Create all tables
    db.create_all()
    
    # Import routes after models to avoid circular imports
    from routes.admin_routes import admin_routes
    
    # Add context processor to check if request is via HTMX
    @app.context_processor
    def utility_processor():
        def is_htmx_request():
            return 'HX-Request' in request.headers
        return {'is_htmx_request': is_htmx_request}
    
    # We're using traditional page loads instead of HTMX
    # for better stability and reliability
    from routes.teacher_routes import teacher_routes
    from routes.auth_routes import auth_routes
    
    # Register blueprints
    app.register_blueprint(admin_routes)
    app.register_blueprint(teacher_routes)
    app.register_blueprint(auth_routes)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_routes.dashboard'))
            else:
                return redirect(url_for('teacher_routes.dashboard'))
        return redirect(url_for('auth_routes.login'))

# Create routes module if it doesn't exist
import os
if not os.path.exists('routes'):
    os.makedirs('routes', exist_ok=True)
    with open('routes/__init__.py', 'w') as f:
        f.write('# Routes package')

if not os.path.exists('routes/admin_routes.py'):
    with open('routes/admin_routes.py', 'w') as f:
        f.write('''
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Teacher, TeacherRoutine, Absence, Substitution, SubstitutionTransfer
from forms import TeacherForm, AbsenceForm
from app import db
from utils import get_current_date, find_substitutes, generate_substitution_plan
import json
from datetime import datetime

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    today = get_current_date()
    absent_count = Absence.query.filter_by(date=today).count()
    teacher_count = Teacher.query.count()
    substitution_count = Substitution.query.filter_by(date=today).count()
    transfer_requests = SubstitutionTransfer.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                          absent_count=absent_count, 
                          teacher_count=teacher_count,
                          substitution_count=substitution_count,
                          transfer_requests=transfer_requests,
                          today=today)

@admin_routes.route('/admin/teachers')
@login_required
def teachers():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    teachers_list = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers_list)

@admin_routes.route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    form = TeacherForm()
    if form.validate_on_submit():
        # Create new teacher record
        teacher = Teacher(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            teacher_id=form.teacher_id.data
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Create user account for the teacher
        from models import User
        from werkzeug.security import generate_password_hash
        
        user = User(
            username=form.email.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.name.data.split()[0]),  # First name as password
            role='teacher',
            teacher_id=teacher.id
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('admin_routes.edit_schedule', teacher_id=teacher.id))
    
    return render_template('admin/teacher_edit.html', form=form, teacher=None)

@admin_routes.route('/admin/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(obj=teacher)
    
    if form.validate_on_submit():
        form.populate_obj(teacher)
        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('admin_routes.teachers'))
    
    return render_template('admin/teacher_edit.html', form=form, teacher=teacher)

@admin_routes.route('/admin/teachers/schedule/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(teacher_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    teacher = Teacher.query.get_or_404(teacher_id)
    
    if request.method == 'POST':
        # Delete existing schedule
        TeacherRoutine.query.filter_by(teacher_id=teacher_id).delete()
        
        # Parse the submitted routine data
        routine_data = json.loads(request.form.get('routine_data', '{}'))
        
        # Save new schedule entries
        for day in routine_data:
            for period_num, period_data in enumerate(routine_data[day], 1):
                if period_data:  # Skip if empty
                    routine_entry = TeacherRoutine(
                        teacher_id=teacher_id,
                        day=day,
                        period=period_num,
                        class_name=period_data.get('class', ''),
                        section=period_data.get('section', ''),
                        is_free=(period_data.get('class', '') == 'Free')
                    )
                    db.session.add(routine_entry)
        
        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('admin_routes.teachers'))
    
    # Get existing schedule or create empty template
    schedule = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = range(1, 9)  # 8 periods
    
    # Initialize empty schedule
    for day in days:
        schedule[day] = [None] * 8  # 8 periods
    
    # Fill in existing data
    routine_entries = TeacherRoutine.query.filter_by(teacher_id=teacher_id).all()
    for entry in routine_entries:
        schedule[entry.day][entry.period-1] = {
            'class': entry.class_name,
            'section': entry.section,
            'is_free': entry.is_free
        }
    
    return render_template('admin/teacher_edit.html', 
                          teacher=teacher, 
                          schedule=schedule,
                          days=days,
                          periods=periods)

@admin_routes.route('/admin/absence', methods=['GET', 'POST'])
@login_required
def mark_absence():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    form = AbsenceForm()
    if form.validate_on_submit():
        # Process the form submission
        date = form.date.data
        day = form.day.data
        selected_teachers = request.form.getlist('selected_teachers')
        
        # Mark all teachers as present initially
        Absence.query.filter_by(date=date).delete()
        
        # Mark selected teachers as absent
        for teacher_id in selected_teachers:
            absence = Absence(
                teacher_id=teacher_id,
                date=date,
                day=day,
                reported_by='admin'
            )
            db.session.add(absence)
        
        db.session.commit()
        
        # Generate substitution plan
        find_substitutes(date, day)
        
        flash('Absence marked and substitution generated successfully!', 'success')
        return redirect(url_for('admin_routes.substitution'))
    
    # Default to today's date
    if not form.date.data:
        form.date.data = datetime.now().date()
    
    teachers = Teacher.query.all()
    return render_template('admin/absence.html', form=form, teachers=teachers)

@admin_routes.route('/admin/substitution')
@login_required
def substitution():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get substitution plan for the date
    plan = generate_substitution_plan(date)
    
    return render_template('admin/substitution.html', 
                          date=date,
                          plan=plan)

@admin_routes.route('/admin/transfer_requests')
@login_required
def transfer_requests():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get pending transfer requests
    transfers = SubstitutionTransfer.query.filter_by(status='pending').all()
    
    return render_template('admin/transfers.html', transfers=transfers)

@admin_routes.route('/admin/approve_transfer/<int:transfer_id>', methods=['POST'])
@login_required
def approve_transfer(transfer_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    transfer = SubstitutionTransfer.query.get_or_404(transfer_id)
    substitution = Substitution.query.get_or_404(transfer.substitution_id)
    
    # Update the substitution assignment
    substitution.teacher_id = transfer.new_teacher_id
    
    # Mark transfer as approved
    transfer.status = 'approved'
    transfer.action_date = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True})

@admin_routes.route('/admin/reject_transfer/<int:transfer_id>', methods=['POST'])
@login_required
def reject_transfer(transfer_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    transfer = SubstitutionTransfer.query.get_or_404(transfer_id)
    transfer.status = 'rejected'
    transfer.action_date = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True})

@admin_routes.route('/admin/history')
@login_required
def history():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get absences history
    absences = Absence.query.order_by(Absence.date.desc()).all()
    
    # Get substitution history
    substitutions = Substitution.query.order_by(Substitution.date.desc()).all()
    
    # Get transfer history
    transfers = SubstitutionTransfer.query.order_by(SubstitutionTransfer.request_date.desc()).all()
    
    return render_template('admin/history.html', 
                          absences=absences,
                          substitutions=substitutions,
                          transfers=transfers)
''')

if not os.path.exists('routes/teacher_routes.py'):
    with open('routes/teacher_routes.py', 'w') as f:
        f.write('''
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Teacher, TeacherRoutine, Absence, Substitution, SubstitutionTransfer
from app import db
from utils import get_current_date, get_day_from_date
from datetime import datetime

teacher_routes = Blueprint('teacher_routes', __name__)

@teacher_routes.route('/teacher/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher' or not current_user.teacher_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    today = get_current_date()
    day = get_day_from_date(today)
    
    # Get teacher information
    teacher = Teacher.query.get(current_user.teacher_id)
    
    # Check if teacher is absent today
    is_absent = Absence.query.filter_by(
        teacher_id=teacher.id,
        date=today
    ).first() is not None
    
    # Get teacher's schedule for today
    schedule = TeacherRoutine.query.filter_by(
        teacher_id=teacher.id,
        day=day
    ).order_by(TeacherRoutine.period).all()
    
    # Get substitutions assigned to the teacher
    substitutions = Substitution.query.filter_by(
        teacher_id=teacher.id,
        date=today
    ).all()
    
    return render_template('teacher/dashboard.html',
                          teacher=teacher,
                          is_absent=is_absent,
                          schedule=schedule,
                          substitutions=substitutions,
                          today=today,
                          day=day)

@teacher_routes.route('/teacher/mark_absent', methods=['POST'])
@login_required
def mark_absent():
    if current_user.role != 'teacher' or not current_user.teacher_id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    today = get_current_date()
    day = get_day_from_date(today)
    
    # Check if already marked absent
    existing = Absence.query.filter_by(
        teacher_id=current_user.teacher_id,
        date=today
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Already marked absent for today'})
    
    # Mark as absent
    absence = Absence(
        teacher_id=current_user.teacher_id,
        date=today,
        day=day,
        reported_by='self'
    )
    db.session.add(absence)
    
    # Trigger substitution assignment
    from utils import find_substitutes
    db.session.commit()
    find_substitutes(today, day)
    
    return jsonify({'success': True, 'message': 'Successfully marked as absent'})

@teacher_routes.route('/teacher/transfer/<int:substitution_id>', methods=['GET', 'POST'])
@login_required
def request_transfer(substitution_id):
    if current_user.role != 'teacher' or not current_user.teacher_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    substitution = Substitution.query.get_or_404(substitution_id)
    
    # Ensure the substitution belongs to the current teacher
    if substitution.teacher_id != current_user.teacher_id:
        flash('This substitution is not assigned to you.', 'danger')
        return redirect(url_for('teacher_routes.dashboard'))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        new_teacher_id = request.form.get('new_teacher_id')
        transfer_all = request.form.get('transfer_all') == 'on'
        
        if not reason or not new_teacher_id:
            flash('Please provide both reason and select a teacher.', 'danger')
            return redirect(url_for('teacher_routes.request_transfer', substitution_id=substitution_id))
        
        # Create transfer request
        transfer = SubstitutionTransfer(
            substitution_id=substitution_id,
            original_teacher_id=current_user.teacher_id,
            new_teacher_id=new_teacher_id,
            reason=reason,
            request_date=datetime.now(),
            status='pending',
            transfer_all=transfer_all
        )
        db.session.add(transfer)
        db.session.commit()
        
        flash('Transfer request submitted successfully!', 'success')
        return redirect(url_for('teacher_routes.dashboard'))
    
    # Get list of available teachers
    teachers = Teacher.query.filter(Teacher.id != current_user.teacher_id).all()
    
    return render_template('teacher/transfer.html',
                          substitution=substitution,
                          teachers=teachers)

@teacher_routes.route('/teacher/schedule')
@login_required
def view_schedule():
    if current_user.role != 'teacher' or not current_user.teacher_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.get(current_user.teacher_id)
    
    # Get full weekly schedule
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    schedule = {}
    
    for day in days:
        schedule[day] = TeacherRoutine.query.filter_by(
            teacher_id=teacher.id,
            day=day
        ).order_by(TeacherRoutine.period).all()
    
    return render_template('teacher/schedule.html',
                          teacher=teacher,
                          schedule=schedule,
                          days=days)
''')

if not os.path.exists('routes/auth_routes.py'):
    with open('routes/auth_routes.py', 'w') as f:
        f.write('''
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from forms import LoginForm
from werkzeug.security import check_password_hash

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
    
    return render_template('auth/login.html', form=form)

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
        user = User.query.filter_by(email=form.email.data, role='teacher').first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('teacher_routes.dashboard'))
        else:
            flash('Invalid teacher credentials', 'danger')
    
    return render_template('teacher/login.html', form=form)

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth_routes.login'))
''')
