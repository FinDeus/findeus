import json
import os
import sys
from datetime import datetime
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import requests
    import openai
    import anthropic
    import yfinance as yf
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Configure API keys
    openai.api_key = os.getenv('OPENAI_API_KEY')
    anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    print(f"[{datetime.now()}] FinDeus Netlify Function initialized successfully")
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'FinDeus API is running on Netlify'
        })
    
    @app.route('/api/ai/query', methods=['POST'])
    def ai_query():
        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query is required'}), 400
            
            query = data['query']
            model_type = data.get('model', 'openai')
            
            if model_type == 'openai':
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": query}],
                    max_tokens=500
                )
                result = response.choices[0].message.content
            elif model_type == 'anthropic':
                response = anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": query}]
                )
                result = response.content[0].text
            else:
                return jsonify({'error': 'Invalid model type'}), 400
            
            return jsonify({
                'response': result,
                'model': model_type,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error in AI query: {str(e)}")
            return jsonify({'error': f'AI query failed: {str(e)}'}), 500
    
    @app.route('/api/market/realtime/<symbol>', methods=['GET'])
    def get_market_data(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return jsonify({
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': info.get('currentPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'changePercent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return jsonify({'error': f'Market data failed: {str(e)}'}), 500
    
    @app.route('/api/market/sentiment/<symbol>', methods=['GET'])
    def get_market_sentiment(symbol):
        try:
            # Simple sentiment analysis based on price movement
            ticker = yf.Ticker(symbol)
            info = ticker.info
            change_percent = info.get('regularMarketChangePercent', 0)
            
            if change_percent > 2:
                sentiment = 'bullish'
            elif change_percent < -2:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            return jsonify({
                'symbol': symbol,
                'sentiment': sentiment,
                'confidence': min(abs(change_percent) * 10, 100),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error getting sentiment: {str(e)}")
            return jsonify({'error': f'Sentiment analysis failed: {str(e)}'}), 500
    
    @app.route('/api/test', methods=['GET'])
    def test_function():
        return jsonify({
            'message': 'Netlify function is working!',
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'python_version': sys.version,
                'openai_key_set': bool(os.getenv('OPENAI_API_KEY')),
                'anthropic_key_set': bool(os.getenv('ANTHROPIC_API_KEY'))
            }
        })
    
    # Catch-all route for debugging
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            'message': 'FinDeus API Function',
            'path': path,
            'method': request.method,
            'available_routes': [
                '/api/health',
                '/api/ai/query',
                '/api/market/realtime/<symbol>',
                '/api/market/sentiment/<symbol>',
                '/api/test'
            ]
        })

except Exception as e:
    print(f"Critical error initializing function: {str(e)}")
    print(traceback.format_exc())
    
    # Create a minimal error app
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'error': 'Function initialization failed',
            'details': str(e),
            'path': path
        }), 500

def handler(event, context):
    """
    Netlify function handler
    """
    try:
        # Convert Netlify event to Flask-compatible format
        from werkzeug.wrappers import Request
        from werkzeug.serving import WSGIRequestHandler
        
        # Create a test client for the Flask app
        with app.test_client() as client:
            # Extract method and path from event
            method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            
            # Handle query parameters
            query_params = event.get('queryStringParameters') or {}
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            
            # Handle request body
            body = event.get('body', '')
            headers = event.get('headers', {})
            
            # Make request to Flask app
            response = client.open(
                path=path,
                method=method,
                data=body,
                headers=headers,
                query_string=query_string
            )
            
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Handler error',
                'details': str(e)
            })
        }

# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=8080) 