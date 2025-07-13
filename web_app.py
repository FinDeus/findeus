#!/usr/bin/env python3
"""
FinDeus Web Platform
===================

Complete web-based FinDeus platform running in your browser.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load environment variables
def load_env():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
    return env_vars

env_vars = load_env()
OPENAI_API_KEY = env_vars.get('OPENAI_API_KEY', '')
PINECONE_API_KEY = env_vars.get('PINECONE_API_KEY', '')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """AI query endpoint - Meta-Controller simulation"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are FinDeus, an advanced AI financial advisor. Provide insightful, actionable financial advice.'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ],
            'max_tokens': 500
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'response': result['choices'][0]['message']['content'],
                'model': 'gpt-4',
                'tokens_used': result['usage']['total_tokens'],
                'confidence': 0.95
            })
        else:
            return jsonify({'error': 'AI service unavailable'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/generate', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for documents"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'text-embedding-3-small',
            'input': text
        }
        
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result['data'][0]['embedding']
            return jsonify({
                'embedding': embedding[:10],  # First 10 dimensions for display
                'dimensions': len(embedding),
                'tokens_used': result['usage']['total_tokens'],
                'full_embedding_length': len(embedding)
            })
        else:
            return jsonify({'error': 'Embedding service unavailable'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/finance/monte-carlo', methods=['POST'])
def monte_carlo_simulation():
    """Monte Carlo portfolio simulation"""
    try:
        data = request.json
        portfolio_value = data.get('portfolio_value', 100000)
        years = data.get('years', 1)
        
        # Simulate Monte Carlo
        random.seed(42)
        scenarios = []
        
        for _ in range(10000):
            annual_return = random.normalvariate(0.08, 0.15)
            final_value = portfolio_value * ((1 + annual_return) ** years)
            scenarios.append({
                'return': annual_return,
                'final_value': final_value
            })
        
        # Calculate statistics
        returns = [s['return'] for s in scenarios]
        values = [s['final_value'] for s in scenarios]
        
        returns.sort()
        values.sort()
        
        expected_return = sum(returns) / len(returns)
        var_95 = returns[int(0.05 * len(returns))]
        max_loss = min(returns)
        
        return jsonify({
            'expected_return': expected_return,
            'var_95': var_95,
            'max_loss': max_loss,
            'scenarios_run': len(scenarios),
            'portfolio_value': portfolio_value,
            'years': years,
            'recommendation': 'MODERATE BUY' if expected_return > 0.05 else 'HOLD'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ideation/generate', methods=['POST'])
def generate_startup_ideas():
    """Generate startup ideas"""
    try:
        data = request.json
        sector = data.get('sector', 'fintech')
        
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': f'You are FinDeus Ideation Engine. Generate innovative {sector} startup ideas with market analysis.'
                },
                {
                    'role': 'user',
                    'content': f'Generate 3 innovative {sector} startup ideas for 2024. For each idea, provide: name, description, target market, and estimated TAM.'
                }
            ],
            'max_tokens': 800
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'ideas': result['choices'][0]['message']['content'],
                'sector': sector,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Ideation service unavailable'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph/query', methods=['POST'])
def graph_query():
    """Knowledge graph query simulation"""
    try:
        data = request.json
        query = data.get('query', '')
        
        # Simulate graph data
        mock_graph = {
            'nodes': [
                {'id': 'apple', 'label': 'Apple Inc.', 'type': 'Company', 'sector': 'Technology'},
                {'id': 'buffett', 'label': 'Warren Buffett', 'type': 'Investor', 'firm': 'Berkshire Hathaway'},
                {'id': 'tesla', 'label': 'Tesla Inc.', 'type': 'Company', 'sector': 'Automotive'},
                {'id': 'musk', 'label': 'Elon Musk', 'type': 'Person', 'role': 'CEO'}
            ],
            'relationships': [
                {'from': 'buffett', 'to': 'apple', 'type': 'INVESTED_IN', 'amount': '$120B'},
                {'from': 'musk', 'to': 'tesla', 'type': 'CEO_OF', 'since': '2008'},
                {'from': 'apple', 'to': 'tesla', 'type': 'COMPETITOR_OF', 'market': 'EV'}
            ]
        }
        
        return jsonify({
            'graph': mock_graph,
            'query': query,
            'node_count': len(mock_graph['nodes']),
            'relationship_count': len(mock_graph['relationships'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'openai': bool(OPENAI_API_KEY),
            'pinecone': bool(PINECONE_API_KEY),
            'web_server': True
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting FinDeus Web Platform...")
    print("📊 Services available:")
    print("   • AI Query Engine")
    print("   • Document Processing")
    print("   • Monte Carlo Simulation")
    print("   • Startup Ideation")
    print("   • Knowledge Graph")
    print()
    print("🌐 Opening in browser: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 