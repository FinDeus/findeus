#!/bin/bash

# FinDeus Netlify Build Script
# This script builds the Python Flask application for Netlify deployment

echo "🚀 Starting FinDeus build process..."

# Check Python version
echo "🐍 Checking Python version..."
python3 --version || python --version

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ No Python found!"
    exit 1
fi

echo "📦 Using Python command: $PYTHON_CMD"

# Upgrade pip
echo "📦 Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install main dependencies
echo "📦 Installing main dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

# Install function dependencies
echo "⚡ Installing Netlify function dependencies..."
if [ -f "netlify/functions/requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r netlify/functions/requirements.txt
else
    echo "⚠️  No function requirements.txt found, skipping..."
fi

# Verify critical imports
echo "🔍 Verifying critical imports..."
$PYTHON_CMD -c "import flask; print('✅ Flask imported successfully')"
$PYTHON_CMD -c "import requests; print('✅ Requests imported successfully')"
$PYTHON_CMD -c "import openai; print('✅ OpenAI imported successfully')"
$PYTHON_CMD -c "import anthropic; print('✅ Anthropic imported successfully')"
$PYTHON_CMD -c "import yfinance; print('✅ YFinance imported successfully')"

# Create static directory if it doesn't exist
echo "📁 Setting up static directory..."
mkdir -p static

# Copy any additional static files
if [ -d "templates" ]; then
    echo "📄 Copying template files..."
    cp -r templates/* static/ 2>/dev/null || echo "⚠️  No template files to copy"
fi

# Verify the function file exists
if [ -f "netlify/functions/app.py" ]; then
    echo "✅ Netlify function file found"
else
    echo "❌ Netlify function file not found!"
    exit 1
fi

# Test the function syntax
echo "🧪 Testing function syntax..."
$PYTHON_CMD -m py_compile netlify/functions/app.py
if [ $? -eq 0 ]; then
    echo "✅ Function syntax is valid"
else
    echo "❌ Function syntax error!"
    exit 1
fi

echo "🎉 Build completed successfully!"
echo "📊 Build summary:"
echo "   • Python version: $($PYTHON_CMD --version)"
echo "   • Static files: $(ls -la static/ 2>/dev/null | wc -l) files"
echo "   • Function file: netlify/functions/app.py"
echo "   • Dependencies: Installed from requirements.txt" 