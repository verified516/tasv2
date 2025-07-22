# PythonAnywhere Deployment Guide

## Free Hosting on PythonAnywhere

PythonAnywhere offers a generous free tier perfect for Python web applications:
- One web app (custom domain on paid plans)
- 512MB disk space
- MySQL database (512MB)
- SSH access (limited)
- No credit card required

### Quick Setup Steps:

1. **Create Free Account:**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Sign up for a free account

2. **Upload Your Code:**
   
   **Option A: Git (Recommended):**
   - Open a Bash console in PythonAnywhere
   ```bash
   cd ~
   git clone https://github.com/yourusername/tasv2.git
   cd tasv2
   ```
   
   **Option B: Upload Files:**
   - Use the Files tab to upload your project files

3. **Install Dependencies:**
   ```bash
   # In PythonAnywhere bash console
   cd ~/tasv2
   pip3.10 install --user -r requirements.txt
   ```

4. **Create Web App:**
   - Go to "Web" tab in dashboard
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select Python 3.10

5. **Configure WSGI File:**
   Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   import os
   
   # Add your project directory to sys.path
   path = '/home/yourusername/tasv2'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   from main import app as application
   
   # Set environment variables
   os.environ['SESSION_SECRET'] = 'your-secret-key-here'
   os.environ['DATABASE_URL'] = 'sqlite:////home/yourusername/tasv2/school.db'
   ```

6. **Configure Static Files:**
   - In Web tab, scroll to "Static files"
   - URL: `/static/`
   - Directory: `/home/yourusername/tasv2/static/`

7. **Set Environment Variables:**
   ```python
   # Add to your WSGI file or create .env file
   import os
   os.environ['SESSION_SECRET'] = 'generate-a-secret-key'
   os.environ['DATABASE_URL'] = 'sqlite:////home/yourusername/tasv2/instance/school.db'
   ```

8. **Reload Web App:**
   - Click "Reload" button in Web tab

### Database Setup:

**Option 1: SQLite (Simplest for free tier):**
```python
# In your WSGI file or config
DATABASE_URL = 'sqlite:////home/yourusername/tasv2/instance/school.db'
```

**Option 2: MySQL (Free tier includes MySQL):**
```python
# Create MySQL database in PythonAnywhere dashboard
# Use connection details provided
DATABASE_URL = 'mysql://username:password@yourusername.mysql.pythonanywhere-services.com/yourusername$dbname'
```

### Directory Structure:
```
/home/yourusername/
├── tasv2/                    # Your project
│   ├── main.py
│   ├── app.py
│   ├── requirements.txt
│   └── ...
└── .local/                   # Installed packages (--user)
```

### Custom Domain (Paid Plans):
- Hacker Plan ($5/month) supports custom domains
- Configure in Web tab → "Custom domains"

### Debugging:
- Check error logs in Web tab → "Log files"
- Use print statements (they appear in error log)
- Enable Flask debug mode (for development only)

### Limitations of Free Tier:
- Only one web app
- No SSH access (only bash console)
- Limited CPU seconds per day
- 512MB disk space
- Custom domains require paid plan

### Upgrading:
- Hacker Plan: $5/month (custom domains, more storage)
- More CPU seconds and features

### Pro Tips:
- Use SQLite for simplicity on free tier
- Monitor CPU usage in dashboard
- Great for learning and small projects
- Excellent Python environment and package support
- Good documentation and community

### Alternative MySQL Configuration:
```python
# If using MySQL instead of SQLite
import pymysql
pymysql.install_as_MySQLdb()

# Update requirements.txt to include:
# PyMySQL>=1.0.0
```

### Sample WSGI File:
```python
#!/usr/bin/python3.10
import sys
import os

# Path to your project
project_home = '/home/yourusername/tasv2'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Environment variables
os.environ['SESSION_SECRET'] = 'your-secret-key-here'
os.environ['DATABASE_URL'] = 'sqlite:////home/yourusername/tasv2/instance/school.db'

from main import app as application

if __name__ == "__main__":
    application.run()
```