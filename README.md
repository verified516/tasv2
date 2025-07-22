# 🏫 School Teacher Arrangement and Substitution Management System

A comprehensive Flask-based web application for managing teacher schedules, absences, and automatic substitution assignments in schools.

## 🌟 Features

### For Administrators:
- 👥 **Teacher Management**: Add, edit, and manage teacher profiles
- 📅 **Schedule Management**: Create and manage weekly teacher routines
- 🚫 **Absence Tracking**: Mark teacher absences and manage substitutions
- 🔄 **Auto-Substitution**: Intelligent algorithm assigns substitute teachers
- 📋 **Transfer Management**: Handle substitution transfer requests
- 📊 **Reporting**: Generate detailed reports and histories

### For Teachers:
- 🎯 **Personal Dashboard**: View schedules and assigned substitutions
- 📖 **Schedule Viewing**: Check weekly routine and class assignments
- 🔄 **Transfer Requests**: Request substitution transfers with reasons
- ⚠️ **Absence Reporting**: Self-report absences (if enabled)
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🚀 Totally Free Hosting

Deploy your School Management System on **totally free** hosting platforms! 

### ⚡ Quick Deploy Options:

| Platform | Database | Best For | Deploy Link |
|----------|----------|----------|-------------|
| **Railway** | PostgreSQL | **Recommended** | [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/E_u0Z8) |
| **Render** | PostgreSQL (90 days) | Demos | [Deploy Guide](deployment/render/README.md) |
| **Fly.io** | PostgreSQL (3GB) | Production | [Deploy Guide](deployment/fly/README.md) |
| **PythonAnywhere** | MySQL/SQLite | Learning | [Deploy Guide](deployment/pythonanywhere/README.md) |

📖 **[Complete Deployment Guide](DEPLOYMENT.md)** - Detailed instructions for all platforms

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Database**: PostgreSQL/MySQL/SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with role-based access control
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: HTML templates with Bootstrap CSS
- **Server**: Gunicorn WSGI server

## 🏃‍♂️ Quick Start

### Local Development:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/verified516/tasv2.git
   cd tasv2
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and secret key
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Visit:** http://localhost:5000

### Production Deployment:

Choose your preferred **free** hosting platform:

- **Railway (Recommended)**: One-click deploy with included PostgreSQL
- **Render**: Free with PostgreSQL for 90 days
- **Fly.io**: 3GB PostgreSQL database included
- **PythonAnywhere**: Great for learning, MySQL included
- **Vercel**: Serverless deployment option

📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

## 🗄️ Database Models

The system uses 6 main database tables:
- **User**: Authentication and user accounts
- **Teacher**: Teacher profile information
- **TeacherRoutine**: Weekly schedules for teachers
- **Absence**: Teacher absence records
- **Substitution**: Substitution assignments
- **SubstitutionTransfer**: Transfer requests between teachers

## 🧠 Smart Substitution Algorithm

When a teacher is absent:
1. System identifies all periods the absent teacher was scheduled
2. Finds available substitute teachers (those with free periods)
3. Assigns substitutions based on availability and workload balance
4. Creates substitution records and notifies relevant parties
5. Allows teachers to request transfers with admin approval

## 🔧 Configuration

### Environment Variables:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-super-secret-random-key
FLASK_ENV=production
```

### Generate Secret Key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Project Structure

```
/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── models.py             # Database models
├── forms.py              # WTF Forms
├── utils.py              # Utility functions
├── config.py             # Configuration settings
├── routes/               # Blueprint routes
│   ├── auth_routes.py    # Authentication
│   ├── admin_routes.py   # Admin dashboard
│   └── teacher_routes.py # Teacher dashboard
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── deployment/          # Hosting configurations
├── scripts/             # Deployment helpers
└── requirements.txt     # Python dependencies
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected against cross-site request forgery
- **Password Hashing**: Secure password storage with Werkzeug
- **Session Security**: Secure session management with Flask-Login
- **Role-Based Access**: Strict access control (admin/teacher roles)
- **Input Validation**: Comprehensive form validation

## 🧪 Testing & Health Checks

```bash
# Run health check
python scripts/health-check.py [optional-url]

# Generate secret key
./scripts/generate-secret.sh

# Deploy helpers
./scripts/deploy-railway.sh
./scripts/deploy-fly.sh
```

## 📈 Scaling & Performance

**Free Tier Performance:**
- ✅ Perfect for schools with up to 50 teachers
- ✅ Handles moderate daily traffic
- ✅ Suitable for development and testing

**Production Considerations:**
- 🏢 Large schools may need paid hosting tiers
- 📊 Database optimization for 100+ teachers
- 🚀 CDN for static assets
- 🔄 Redis for session storage

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support & Help

- 📖 [Deployment Guide](DEPLOYMENT.md) - Complete hosting instructions
- 🐛 [Issues](https://github.com/verified516/tasv2/issues) - Report bugs or request features
- 💬 [Discussions](https://github.com/verified516/tasv2/discussions) - Ask questions and share ideas

## 🎯 Perfect For

- 🏫 **Schools** - Primary, secondary, and higher education institutions
- 👨‍🏫 **Administrators** - Streamline teacher schedule management
- 📚 **Educational Projects** - Learn modern web development
- 🚀 **Portfolio** - Showcase full-stack development skills

---

**🌟 Star this repository if it helps your school manage teacher schedules better!**

**💰 Deploy for FREE on Railway: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/E_u0Z8)**