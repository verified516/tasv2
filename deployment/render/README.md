# Render.com Deployment Guide

## Free Hosting on Render.com

Render.com offers free hosting for web services and PostgreSQL databases with the following limits:
- Web Services: 750 hours/month (about 1 app running 24/7)
- PostgreSQL: 1GB storage, 1 month retention
- Automatic SSL certificates
- Custom domains supported

### Quick Deploy Steps:

1. **Fork this repository** to your GitHub account

2. **Create account** at [render.com](https://render.com) and connect your GitHub

3. **Create PostgreSQL Database:**
   - Go to Dashboard → New → PostgreSQL
   - Name: `school-management-db`
   - Plan: Free
   - Note down the connection details

4. **Create Web Service:**
   - Go to Dashboard → New → Web Service
   - Connect your forked repository
   - Name: `school-management-system`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app`

5. **Set Environment Variables:**
   - `DATABASE_URL`: Use the Internal Database URL from your PostgreSQL service
   - `SESSION_SECRET`: Generate a random secret key

6. **Deploy:** Click "Create Web Service"

### Using render.yaml (Recommended):

1. Copy `deployment/render/render.yaml` to your repository root
2. Create a new Blueprint on Render
3. Connect your repository - Render will automatically detect the YAML file

### Environment Variables:
```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
SESSION_SECRET=your-super-secret-key-here
```

### Free Limits:
- 512 MB RAM
- 750 build minutes/month
- Database shuts down after 90 days of inactivity
- Web service spins down after 15 minutes of inactivity

### Upgrading Database:
The free PostgreSQL database expires after 90 days. For production use, consider:
- Paid Render PostgreSQL ($7/month)
- External services like ElephantSQL, Aiven, or Neon (some offer free tiers)