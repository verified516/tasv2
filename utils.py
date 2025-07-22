from datetime import datetime, date
from app import db

def get_current_date():
    """Get the current date in the format YYYY-MM-DD."""
    return datetime.now().date()

def get_day_from_date(date_obj):
    """Get the day name from a date object."""
    days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 1", "Day 1"]
    # Python's weekday() returns 0 for Monday and 6 for Sunday
    weekday = date_obj.weekday()
    # Convert to school days (only Day 1 to Day 5)
    if weekday >= 5:  # Weekend
        return "Day 1"  # Default to Day 1 for weekend
    return days[weekday]

def find_substitutes(date_str, day):
    """
    Algorithm to find substitutes for absent teachers.
    
    1. Get all absent teachers for the given date
    2. For each absent teacher, get their schedule for the day
    3. For each period in their schedule, find teachers who are free at that time
    4. Assign a substitute teacher from the available free teachers
    """
    # Convert string date to date object if needed
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date_obj = date_str
    
    # Import models here to avoid circular imports
    from models import Teacher, TeacherRoutine, Absence, Substitution
    
    # Clear existing substitutions for this date
    Substitution.query.filter_by(date=date_obj).delete()
    db.session.commit()
    
    # Get absent teachers
    absences = Absence.query.filter_by(date=date_obj).all()
    
    # Process each absent teacher
    for absence in absences:
        # Get the absent teacher's schedule for the day
        absent_teacher_routines = TeacherRoutine.query.filter_by(
            teacher_id=absence.teacher_id,
            day=day,
            is_free=False  # Only handle actual classes, not free periods
        ).all()
        
        # For each class that needs a substitute
        for routine in absent_teacher_routines:
            # Find teachers who are free during this period
            free_teachers = Teacher.query.join(TeacherRoutine).filter(
                TeacherRoutine.day == day,
                TeacherRoutine.period == routine.period,
                TeacherRoutine.is_free == True,
                Teacher.id != absence.teacher_id  # Exclude the absent teacher
            ).all()
            
            # Create a list of available teachers
            available_teachers = list(free_teachers)
            
            # Add teachers who don't have any routine for this period
            all_teachers = Teacher.query.all()
            teachers_with_routines = [t.teacher_id for t in TeacherRoutine.query.filter_by(
                day=day,
                period=routine.period
            ).all()]
            
            for teacher in all_teachers:
                if teacher.id not in [t.id for t in available_teachers] and \
                   teacher.id != absence.teacher_id and \
                   teacher.id not in teachers_with_routines:
                    available_teachers.append(teacher)
            
            # If there are available teachers, assign the first one as substitute
            if available_teachers:
                substitute_teacher = available_teachers[0]
                
                # Create substitution record
                substitution = Substitution(
                    original_teacher_id=absence.teacher_id,
                    teacher_id=substitute_teacher.id,
                    date=date_obj,
                    day=day,
                    period=routine.period,
                    class_name=routine.class_name,
                    section=routine.section
                )
                db.session.add(substitution)
                db.session.commit()

def generate_substitution_plan(date_str):
    """
    Generate a complete substitution plan for the given date.
    Returns a dictionary organized by period with all substitution details.
    """
    # Convert string date to date object if needed
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date_obj = date_str
    
    # Import models here to avoid circular imports
    from models import Substitution, SubstitutionTransfer
    
    # Get all substitutions for this date
    substitutions = Substitution.query.filter_by(date=date_obj).order_by(Substitution.period).all()
    
    # Organize substitutions by period
    plan = {}
    for period in range(1, 9):  # 8 periods
        period_subs = []
        for sub in substitutions:
            if sub.period == period:
                # Check if there are pending transfer requests for this substitution
                transfer_count = SubstitutionTransfer.query.filter_by(
                    substitution_id=sub.id,
                    status='pending'
                ).count()
                
                # Add substitution details
                period_subs.append({
                    'id': sub.id,
                    'original_teacher': sub.original_teacher.name,
                    'substitute_teacher': sub.substitute_teacher.name,
                    'class_name': sub.class_name,
                    'section': sub.section,
                    'transfer_requests': transfer_count
                })
        
        plan[period] = period_subs
    
    return plan