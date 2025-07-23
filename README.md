# School Management System - Complete Application Guide

## Overview
This is a comprehensive school management system built with Flask (Python) that handles teacher substitution and absence tracking. The system provides role-based access for administrators and teachers with automated substitution assignment capabilities.

## Application Architecture

### Technology Stack
- **Backend Framework**: Flask (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with role-based access control
- **Frontend**: HTML templates with Bootstrap CSS framework
- **Forms**: Flask-WTF for form handling and CSRF protection
- **Server**: Gunicorn WSGI server

### Project Structure
```
/
├── app.py                  # Main Flask application configuration
├── main.py                 # Application entry point
├── models.py               # Database models (User, Teacher, etc.)
├── forms.py                # WTF Forms for user input
├── utils.py                # Utility functions
├── config.py               # Configuration settings
├── routes/                 # Blueprint routes
│   ├── auth_routes.py      # Authentication routes
│   ├── admin_routes.py     # Admin dashboard routes
│   └── teacher_routes.py   # Teacher dashboard routes
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── auth/               # Login/authentication templates
│   ├── admin/              # Admin dashboard templates
│   └── teacher/            # Teacher dashboard templates
└── static/                 # CSS, JS, and static assets
    ├── css/
    └── js/
```

## How the Application Works

### 1. Authentication System
- **User Registration**: Creates user accounts linked to teacher profiles
- **Role-Based Access**: Two main roles - 'admin' and 'teacher'
- **Login System**: Separate login flows for admin and teachers
- **Session Management**: Secure session handling with Flask-Login

### 2. Core Features

#### For Administrators:
- **Teacher Management**: Add, edit, and manage teacher profiles
- **Schedule Management**: Create and manage teacher routines/schedules
- **Absence Tracking**: Record teacher absences and manage substitutions
- **Substitution Assignment**: Automatically assign substitute teachers based on availability
- **Transfer Requests**: Handle teacher substitution transfer requests
- **Reporting**: Generate PDF reports for schedules and substitutions

#### For Teachers:
- **Personal Dashboard**: View personal schedule and assigned substitutions
- **Schedule Viewing**: Check weekly routine and class assignments
- **Substitution Requests**: Request transfers of assigned substitutions
- **Absence Reporting**: Self-report absences (if enabled)

### 3. Database Models

The system uses 6 main database tables:

1. **User**: Authentication and user accounts
2. **Teacher**: Teacher profile information
3. **TeacherRoutine**: Weekly schedules for teachers
4. **Absence**: Teacher absence records
5. **Substitution**: Substitution assignments
6. **SubstitutionTransfer**: Transfer requests between teachers

### 4. Key Algorithms

#### Substitution Assignment Algorithm
When a teacher is absent, the system:
1. Identifies all periods the absent teacher was scheduled to teach
2. Finds available substitute teachers (those with free periods)
3. Assigns substitutions based on availability and workload balance
4. Creates substitution records in the database
5. Notifies relevant parties

#### Transfer Request System
Teachers can request to transfer substitutions to other available teachers:
1. Teacher submits transfer request with reason
2. Admin reviews and approves/rejects the request
3. If approved, substitution is reassigned to the new teacher
4. All parties are notified of the change

## Application Flow

### 1. Startup Process
```python
# main.py starts the application
from app import app

# app.py initializes:
- Flask application
- Database connection
- Authentication system
- Routes registration
- Database table creation
```

### 2. Request Processing
1. **URL Routing**: Flask routes requests to appropriate blueprint handlers
2. **Authentication Check**: Flask-Login verifies user authentication
3. **Role Verification**: Routes check user roles for access control
4. **Form Processing**: WTF forms handle user input validation
5. **Database Operations**: SQLAlchemy ORM handles database interactions
6. **Template Rendering**: Jinja2 renders HTML responses

### 3. Data Flow
```
User Input → Forms → Routes → Business Logic → Database → Templates → Response
```

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL database connection string
- `SESSION_SECRET`: Secret key for session encryption

### Database Configuration
- **Connection Pool**: 300-second recycle time with pre-ping enabled
- **CSRF Protection**: Enabled for all forms
- **Cascade Deletions**: Configured for data integrity

## Security Features

1. **CSRF Protection**: All forms protected against cross-site request forgery
2. **Password Hashing**: Secure password storage using Werkzeug
3. **Session Security**: Secure session management with Flask-Login
4. **Role-Based Access**: Strict access control based on user roles
5. **Input Validation**: Form validation prevents malicious input

## Running the Application

### Development Mode
```bash
python main.py
# Runs on http://0.0.0.0:5000 with debug mode enabled
```

### Production Mode
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
# Uses Gunicorn WSGI server for production deployment
```

## Key Features in Detail

### 1. Dynamic Scheduling
- Flexible weekly schedule management
- Support for multiple periods per day
- Free period tracking for substitution availability

### 2. Automated Substitution
- Smart algorithm assigns substitutes based on availability
- Prevents over-assignment and ensures fair distribution
- Handles complex scheduling constraints

### 3. Transfer System
- Teachers can request substitution transfers
- Admin approval workflow
- Option to transfer all substitutions for a day

### 4. Reporting System
- PDF generation for schedules and reports
- Detailed substitution tracking
- Historical absence data

## API Endpoints

### Authentication Routes
- `GET/POST /login` - Main login page
- `GET/POST /admin/login` - Admin-specific login
- `GET/POST /teacher/login` - Teacher-specific login
- `GET /logout` - Logout functionality

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET/POST /admin/teachers` - Teacher management
- `GET/POST /admin/schedule` - Schedule management
- `GET/POST /admin/absences` - Absence management
- `GET /admin/substitutions` - Substitution overview

### Teacher Routes
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/schedule` - Personal schedule view
- `GET /teacher/substitutions` - Assigned substitutions
- `POST /teacher/transfer` - Request substitution transfer

## Error Handling

The application includes comprehensive error handling:
- Database connection errors
- Form validation errors
- Authentication failures
- Route protection for unauthorized access
- Graceful degradation for missing data

## Future Enhancements

Potential areas for expansion:
- SMS/Email notifications
- Mobile-responsive design improvements
- Advanced reporting and analytics
- Integration with school information systems
- Calendar synchronization
- Automated absence detection
