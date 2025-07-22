# Railway.app Deployment Guide

## Free Hosting on Railway.app

Railway offers generous free hosting with:
- $5 in free credits monthly
- PostgreSQL database included
- Automatic deployments from GitHub
- Custom domains
- No sleep mode (unlike Heroku)

### Quick Deploy Steps:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/E_u0Z8?referralCode=bonus)

**Or Manual Setup:**

1. **Create account** at [railway.app](https://railway.app)

2. **Fork this repository** to your GitHub account

3. **Create New Project:**
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your forked repository

4. **Add PostgreSQL Database:**
   - In your project dashboard, click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway will automatically set DATABASE_URL

5. **Configure Environment Variables:**
   - Go to your web service → "Variables"
   - Add: `SESSION_SECRET=your-random-secret-key`

6. **Deploy:** Railway will automatically build and deploy

### Using railway.toml (Optional):

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app"

[[services]]
name = "web"

[[services]]
name = "postgres"
```

### Environment Variables Setup:
Railway automatically provides these when you add PostgreSQL:
- `DATABASE_URL` - Automatically set by Railway PostgreSQL service
- `DATABASE_PRIVATE_URL` - Internal connection URL

You need to add:
- `SESSION_SECRET` - Your application secret key

### Free Usage Limits:
- $5 worth of usage per month (typically covers 24/7 small app)
- Automatic scaling
- Usage-based pricing after free credits

### Custom Domain:
1. Go to your service → "Settings" → "Domains"
2. Add your custom domain
3. Configure DNS as instructed

### Pro Tips:
- Railway automatically detects Python and installs requirements.txt
- Database backups available in paid plans
- Excellent for development and small production apps
- No cold starts like other free services