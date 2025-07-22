#!/bin/bash

# Railway Deployment Helper Script
# Make sure you have Railway CLI installed: https://docs.railway.app/develop/cli

echo "🚂 Railway Deployment Helper"
echo "=============================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"

# Login check
if ! railway whoami &> /dev/null; then
    echo "🔑 Please login to Railway:"
    railway login
fi

echo "👤 Logged in as: $(railway whoami)"

# Initialize project
echo "📁 Initializing Railway project..."
railway login

read -p "Enter your project name (e.g., school-management): " PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME="school-management-system"
fi

# Create project
echo "🚀 Creating new Railway project: $PROJECT_NAME"
railway project create --name "$PROJECT_NAME"

# Add PostgreSQL
echo "🗄️ Adding PostgreSQL database..."
railway add --database postgresql

# Generate and set secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
echo "🔐 Setting SESSION_SECRET..."
railway variables set SESSION_SECRET="$SECRET_KEY"

echo ""
echo "✅ Railway setup complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub if you haven't already"
echo "2. Connect your GitHub repo in Railway dashboard"  
echo "3. Or deploy directly: railway up"
echo ""
echo "Your app will be available at: https://$PROJECT_NAME.up.railway.app"
echo ""
echo "🎉 Happy hosting!"