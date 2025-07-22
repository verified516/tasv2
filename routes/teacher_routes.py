
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from routes import render_template_with_htmx as render_template
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
