#!/bin/bash

# Fly.io Deployment Helper Script  
# Make sure you have Fly CLI installed: https://fly.io/docs/hands-on/install-flyctl/

echo "🚁 Fly.io Deployment Helper"
echo "============================"

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly CLI not found. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    echo "   Or visit: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

echo "✅ Fly CLI found"

# Login check
if ! flyctl auth whoami &> /dev/null; then
    echo "🔑 Please login to Fly.io:"
    flyctl auth signup
fi

echo "👤 Logged in as: $(flyctl auth whoami)"

# Copy Fly configuration
echo "📁 Copying Fly.io configuration files..."
cp deployment/fly/fly.toml ./
cp deployment/fly/Dockerfile ./

read -p "Enter your app name (e.g., school-management): " APP_NAME
if [ -z "$APP_NAME" ]; then
    APP_NAME="school-management-$(date +%s)"
fi

# Update fly.toml with app name
sed -i "s/app = \"school-management\"/app = \"$APP_NAME\"/" fly.toml

# Launch app
echo "🚀 Launching Fly.io app: $APP_NAME"
flyctl launch --copy-config --name "$APP_NAME" --no-deploy

# Create PostgreSQL database
echo "🗄️ Creating PostgreSQL database..."
read -p "Enter database name (default: ${APP_NAME}-db): " DB_NAME
if [ -z "$DB_NAME" ]; then
    DB_NAME="${APP_NAME}-db"
fi

flyctl postgres create --name "$DB_NAME" --region iad
flyctl postgres attach "$DB_NAME" --app "$APP_NAME"

# Generate and set secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
echo "🔐 Setting SESSION_SECRET..."
flyctl secrets set SESSION_SECRET="$SECRET_KEY" --app "$APP_NAME"

# Deploy
echo "🚀 Deploying application..."
flyctl deploy --app "$APP_NAME"

echo ""
echo "✅ Fly.io deployment complete!"
echo ""
echo "Your app is available at: https://${APP_NAME}.fly.dev"
echo ""
echo "Useful commands:"
echo "  flyctl logs --app $APP_NAME         # View logs"
echo "  flyctl status --app $APP_NAME       # Check status"  
echo "  flyctl ssh console --app $APP_NAME  # SSH into app"
echo ""
echo "🎉 Happy flying!"