#!/usr/bin/python3.10

import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/tasv2'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['SESSION_SECRET'] = 'CHANGE-THIS-TO-A-RANDOM-SECRET-KEY'
os.environ['DATABASE_URL'] = 'sqlite:////home/yourusername/tasv2/instance/school.db'

# Import your Flask app
from main import app as application

if __name__ == "__main__":
    application.run()