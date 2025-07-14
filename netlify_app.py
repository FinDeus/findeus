#!/usr/bin/env python3
"""
FinDeus Financial Platform - Netlify Serverless Version
A simplified version of the Flask app optimized for Netlify deployment
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import openai
import anthropic
import threading
import time
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# API Keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

# Initialize API clients
openai_client = None
anthropic_client = None

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    openai_client = openai

if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Cache for market data
cache = {}
cache_lock = threading.Lock()
CACHE_DURATION = 300  # 5 minutes

def cache_result(duration=CACHE_DURATION):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            with cache_lock:
                if cache_key in cache:
                    result, timestamp = cache[cache_key]
                    if time.time() - timestamp < duration:
                        return result
                
                result = func(*args, **kwargs)
                cache[cache_key] = (result, time.time())
                return result
        return wrapper
    return decorator

# Health Check Endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    services = {
        'openai': bool(OPENAI_API_KEY),
        'anthropic': bool(ANTHROPIC_API_KEY),
        'pinecone': bool(PINECONE_API_KEY),
        'yfinance': True
    }
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': services,
        'version': '1.0.0'
    })

# Market Data Endpoints
@app.route('/api/market/realtime/<symbol>', methods=['GET'])
@cache_result(60)  # Cache for 1 minute
def get_realtime_data(symbol):
    """Get real-time market data"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        return jsonify({
            'symbol': symbol.upper(),
            'name': info.get('longName', symbol.upper()),
            'price': info.get('currentPrice', 0),
            'change': info.get('regularMarketChange', 0),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('regularMarketVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting realtime data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# AI Query Endpoint
@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """Process AI queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        model = data.get('model', 'gpt-4')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if model.startswith('gpt') and openai_client:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a financial AI assistant. Provide helpful, accurate financial advice and analysis."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return jsonify({
                'response': response.choices[0].message.content,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
        
        elif model.startswith('claude') and anthropic_client:
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": f"As a financial AI assistant, please help with: {query}"}
                ]
            )
            
            return jsonify({
                'response': response.content[0].text,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
        
        else:
            return jsonify({'error': 'Model not available or API key missing'}), 400
    
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Document Processing
@app.route('/api/embeddings/generate', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for documents"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if not openai_client:
            return jsonify({'error': 'OpenAI API key not configured'}), 400
        
        # Generate embeddings
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        embedding = response.data[0].embedding
        
        return jsonify({
            'text': text[:100] + '...' if len(text) > 100 else text,
            'embedding_dimension': len(embedding),
            'embedding': embedding,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 