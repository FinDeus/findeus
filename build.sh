#!/bin/bash

# FinDeus Netlify Build Script
# This script builds the Python Flask application for Netlify deployment

echo "🚀 Starting FinDeus build process..."

# Set up Python environment
echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Verify static files exist
echo "📁 Verifying static files..."
if [ ! -d "static" ]; then
    echo "❌ Static directory not found!"
    exit 1
fi

if [ ! -f "static/index.html" ]; then
    echo "❌ Static index.html not found!"
    exit 1
fi

# Verify Netlify functions exist
echo "⚡ Verifying Netlify functions..."
if [ ! -d "netlify/functions" ]; then
    echo "❌ Netlify functions directory not found!"
    exit 1
fi

if [ ! -f "netlify/functions/app.py" ]; then
    echo "❌ Netlify function app.py not found!"
    exit 1
fi

# Verify core Python files exist
echo "🐍 Verifying Python application files..."
if [ ! -f "netlify_app.py" ]; then
    echo "❌ netlify_app.py not found!"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "🌐 Ready for Netlify deployment!" 