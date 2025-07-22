#!/bin/bash

# Environment Setup Helper Script

echo "🛠️ School Management System Setup"
echo "================================="
echo ""

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "🐍 Python version: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    
    # Update .env file with generated secret
    sed -i "s/your-super-secret-random-key-here/$SECRET_KEY/" .env
    
    echo "🔐 Generated SESSION_SECRET and saved to .env"
    echo "📝 Please edit .env file and set your DATABASE_URL"
else
    echo "✅ .env file already exists"
fi

# Test the setup
echo ""
echo "🧪 Testing setup..."
python scripts/health-check.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database URL"
echo "2. Run: python main.py"
echo "3. Visit: http://localhost:5000"
echo ""
echo "For deployment, see: DEPLOYMENT.md"