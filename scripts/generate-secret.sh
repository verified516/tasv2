#!/bin/bash

# Generate Secret Key Helper Script

echo "🔐 Secret Key Generator"
echo "======================="
echo ""

echo "Choose your method:"
echo "1. Python (recommended)"
echo "2. OpenSSL"
echo "3. Node.js"
echo "4. Online generator"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        if command -v python3 &> /dev/null; then
            SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
            echo ""
            echo "🐍 Generated with Python:"
            echo "$SECRET_KEY"
        elif command -v python &> /dev/null; then
            SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
            echo ""
            echo "🐍 Generated with Python:"
            echo "$SECRET_KEY"
        else
            echo "❌ Python not found. Try another method."
        fi
        ;;
    2)
        if command -v openssl &> /dev/null; then
            SECRET_KEY=$(openssl rand -base64 32)
            echo ""
            echo "🔒 Generated with OpenSSL:"
            echo "$SECRET_KEY"
        else
            echo "❌ OpenSSL not found. Try another method."
        fi
        ;;
    3)
        if command -v node &> /dev/null; then
            SECRET_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")
            echo ""
            echo "🟢 Generated with Node.js:"
            echo "$SECRET_KEY"
        else
            echo "❌ Node.js not found. Try another method."
        fi
        ;;
    4)
        echo ""
        echo "🌐 Opening online generator..."
        echo "Visit: https://passwordsgenerator.net/"
        echo "Or: https://generate-secret.vercel.app/"
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "https://passwordsgenerator.net/"
        elif command -v open &> /dev/null; then
            open "https://passwordsgenerator.net/"
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "💡 Use this key as your SESSION_SECRET environment variable"
echo "   Example: SESSION_SECRET=$SECRET_KEY"
echo ""
echo "⚠️  Keep this key secret and don't commit it to version control!"