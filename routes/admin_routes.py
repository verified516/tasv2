
from flask import Blueprint, request, redirect, url_for, flash, jsonify, current_app
from routes import render_template_with_htmx as render_template
from flask_login import login_required, current_user
from models import Teacher, TeacherRoutine, Absence, Substitution, SubstitutionTransfer, User
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
    
    # Set the teacher ID for validation
    form._teacher_id = teacher_id
    
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
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5']
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
    
    # For debugging
    if request.method == 'POST':
        current_app.logger.debug(f"Form data received: {request.form}")
        current_app.logger.debug(f"Request headers: {request.headers}")
        selected_teachers = request.form.getlist('selected_teachers')
        current_app.logger.debug(f"Selected teachers: {selected_teachers}")
    
    if form.validate_on_submit():
        # Process the form submission
        date = form.date.data
        day = form.day.data
        selected_teachers = request.form.getlist('selected_teachers')
        
        current_app.logger.info(f"Processing absence form. Date: {date}, Day: {day}, Selected teachers: {selected_teachers}")
        
        try:
            # Mark all teachers as present initially
            deleted_count = Absence.query.filter_by(date=date).delete()
            current_app.logger.info(f"Deleted {deleted_count} previous absence records")
            
            # Mark selected teachers as absent
            added_count = 0
            for teacher_id in selected_teachers:
                try:
                    # Convert to integer since form data comes as strings
                    teacher_id_int = int(teacher_id)
                    
                    # Check if teacher exists
                    teacher = Teacher.query.get(teacher_id_int)
                    if teacher:
                        absence = Absence(
                            teacher_id=teacher_id_int,
                            date=date,
                            day=day,
                            reported_by='admin'
                        )
                        db.session.add(absence)
                        added_count += 1
                    else:
                        current_app.logger.error(f"Teacher with ID {teacher_id_int} not found")
                except ValueError:
                    current_app.logger.error(f"Invalid teacher ID format: {teacher_id}")
                    continue
            
            db.session.commit()
            current_app.logger.info(f"Added {added_count} new absence records")
            
            # Generate substitution plan
            try:
                find_substitutes(date, day)
                current_app.logger.info("Substitution plan generated successfully")
            except Exception as e:
                current_app.logger.error(f"Error generating substitution plan: {str(e)}")
                db.session.rollback()
                flash('Error generating substitution plan. Please try again.', 'danger')
                
                # Handle AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Error generating substitution plan. Please try again.'
                    }), 400
                return redirect(url_for('admin_routes.mark_absence'))
            
            flash('Absence marked and substitution generated successfully!', 'success')
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'redirect': url_for('admin_routes.substitution')
                })
            return redirect(url_for('admin_routes.substitution'))
        except Exception as e:
            current_app.logger.error(f"Error processing absence form: {str(e)}")
            db.session.rollback()
            flash('An error occurred while processing absences. Please try again.', 'danger')
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'An error occurred while processing absences. Please try again.'
                }), 500
    elif request.method == 'POST':
        # If form validation failed
        current_app.logger.error(f"Form validation errors: {form.errors}")
        flash('Please correct the errors in the form.', 'danger')
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Please correct the errors in the form.',
                'errors': form.errors
            }), 400
    
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

@admin_routes.route('/admin/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        teacher = Teacher.query.get_or_404(teacher_id)
        
        # Delete associated user if it exists
        user = User.query.filter_by(teacher_id=teacher_id).first()
        if user:
            db.session.delete(user)
        
        # Teacher model has cascade relationships configured, 
        # so this should delete routines, absences, and substitutions
        db.session.delete(teacher)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting teacher: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

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
