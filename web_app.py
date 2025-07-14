#!/usr/bin/env python3
"""
FinDeus - Advanced Financial Intelligence Platform
=================================================
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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
OPENAI_API_KEY = env_vars.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = env_vars.get('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_API_KEY', '')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ai_engine': 'operational',
            'market_data': 'operational',
            'analytics': 'operational'
        }
    })

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """AI query endpoint"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Simulate AI processing
        time.sleep(0.5)
        
        # Generate contextual response based on query
        if 'market' in query.lower() or 'stock' in query.lower():
            response = f"Based on current market analysis, here's my assessment of '{query}': The market shows mixed signals with volatility expected. Key indicators suggest cautious optimism for the next quarter. Technical analysis reveals support levels holding, but watch for potential resistance at current levels."
        elif 'portfolio' in query.lower() or 'investment' in query.lower():
            response = f"Portfolio analysis for '{query}': Diversification remains key. Current allocation shows 60% equities, 30% bonds, 10% alternatives. Risk-adjusted returns are within target parameters. Consider rebalancing if equity allocation exceeds 65%."
        elif 'risk' in query.lower():
            response = f"Risk assessment for '{query}': Current risk metrics show moderate exposure. VaR calculations suggest 2.3% daily risk. Stress testing indicates portfolio resilience under various scenarios. Consider hedging strategies for downside protection."
        else:
            response = f"Financial analysis for '{query}': Based on comprehensive data analysis, multiple factors indicate this requires careful consideration. Market conditions, economic indicators, and risk metrics all play crucial roles in this assessment. Recommend further analysis before making decisions."
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.85,
            'sources': ['Market Data', 'Technical Analysis', 'Risk Models']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/data/<symbol>')
def market_data(symbol):
    """Market data endpoint"""
    try:
        # Simulate market data
        base_price = 150 + random.uniform(-50, 50)
        change = random.uniform(-5, 5)
        change_percent = (change / base_price) * 100
        
        return jsonify({
            'symbol': symbol.upper(),
            'price': round(base_price + change, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'volume': random.randint(1000000, 10000000),
            'timestamp': datetime.now().isoformat(),
            'market_cap': f"${random.randint(10, 500)}B",
            'pe_ratio': round(random.uniform(15, 35), 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/analyze', methods=['POST'])
def portfolio_analyze():
    """Portfolio analysis endpoint"""
    try:
        data = request.json
        holdings = data.get('holdings', [])
        
        if not holdings:
            return jsonify({'error': 'Holdings data required'}), 400
        
        # Simulate portfolio analysis
        total_value = sum(float(h.get('value', 0)) for h in holdings)
        
        analysis = {
            'total_value': round(total_value, 2),
            'total_return': round(random.uniform(-5, 15), 2),
            'risk_score': round(random.uniform(3, 8), 1),
            'diversification_score': round(random.uniform(6, 9), 1),
            'sectors': [
                {'name': 'Technology', 'percentage': 35},
                {'name': 'Healthcare', 'percentage': 20},
                {'name': 'Finance', 'percentage': 25},
                {'name': 'Consumer', 'percentage': 20}
            ],
            'recommendations': [
                'Consider reducing tech exposure',
                'Increase international diversification',
                'Add defensive positions'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/risk', methods=['POST'])
def risk_analysis():
    """Risk analysis endpoint"""
    try:
        data = request.json
        portfolio = data.get('portfolio', {})
        
        # Simulate risk calculations
        var_95 = round(random.uniform(2, 8), 2)
        var_99 = round(random.uniform(4, 12), 2)
        sharpe_ratio = round(random.uniform(0.8, 2.2), 2)
        
        risk_metrics = {
            'var_95': var_95,
            'var_99': var_99,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': round(random.uniform(8, 25), 2),
            'volatility': round(random.uniform(12, 28), 2),
            'beta': round(random.uniform(0.7, 1.3), 2),
            'risk_grade': 'B+' if var_95 < 5 else 'B' if var_95 < 7 else 'C+',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(risk_metrics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/forecast', methods=['POST'])
def forecast():
    """Market forecast endpoint"""
    try:
        data = request.json
        symbol = data.get('symbol', 'MARKET')
        days = int(data.get('days', 30))
        
        # Generate forecast data
        current_price = 150 + random.uniform(-50, 50)
        forecast_data = []
        
        for i in range(days):
            date = datetime.now().strftime('%Y-%m-%d')
            price = current_price * (1 + random.uniform(-0.03, 0.03))
            forecast_data.append({
                'date': date,
                'price': round(price, 2),
                'confidence': round(random.uniform(0.6, 0.9), 2)
            })
            current_price = price
        
        return jsonify({
            'symbol': symbol,
            'forecast': forecast_data,
            'trend': 'bullish' if forecast_data[-1]['price'] > forecast_data[0]['price'] else 'bearish',
            'accuracy': round(random.uniform(0.7, 0.85), 2),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting FinDeus Financial Intelligence Platform...")
    print("📊 Core Services:")
    print("   • AI Query Engine")
    print("   • Real-time Market Data")
    print("   • Portfolio Analysis")
    print("   • Risk Assessment")
    print("   • Predictive Analytics")
    print()
    print("🌐 Server running at: http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 