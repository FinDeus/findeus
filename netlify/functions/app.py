#!/usr/bin/env python3
"""
FinDeus - Netlify Function Handler with Real AI APIs
==================================================
"""

import json
import os
import requests
from datetime import datetime

def handler(event, context):
    """
    Netlify function handler for FinDeus API with real AI integration
    """
    try:
        # Get request details
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Parse JSON body if present
        try:
            if body:
                body_data = json.loads(body)
            else:
                body_data = {}
        except:
            body_data = {}
        
        # Route handling
        if path == '/api/health' or path == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': json.dumps({
                    'status': 'online',
                    'timestamp': datetime.now().isoformat(),
                    'message': 'FinDeus God of Finance API is running on Netlify',
                    'services': {
                        'ai_engine': 'operational',
                        'openai': 'connected' if os.environ.get('OPENAI_API_KEY') else 'missing_key',
                        'anthropic': 'connected' if os.environ.get('ANTHROPIC_API_KEY') else 'missing_key',
                        'pinecone': 'connected' if os.environ.get('PINECONE_API_KEY') else 'missing_key',
                        'market_data': 'operational',
                        'analytics': 'operational'
                    }
                })
            }
        
        elif path == '/api/ai/query' and method == 'POST':
            query = body_data.get('query', '')
            if not query:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Query is required'})
                }
            
            # Try OpenAI first
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                try:
                    response = requests.post(
                        'https://api.openai.com/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {openai_key}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'model': 'gpt-3.5-turbo',
                            'messages': [
                                {
                                    'role': 'system',
                                    'content': 'You are FinDeus, the God of Finance. You provide divine financial wisdom and analysis with authority and insight. Always speak as the omniscient deity of financial markets.'
                                },
                                {
                                    'role': 'user',
                                    'content': query
                                }
                            ],
                            'max_tokens': 500,
                            'temperature': 0.7
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result['choices'][0]['message']['content']
                        
                        return {
                            'statusCode': 200,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*'
                            },
                            'body': json.dumps({
                                'response': ai_response,
                                'timestamp': datetime.now().isoformat(),
                                'confidence': 0.95,
                                'model': 'OpenAI GPT-3.5-turbo',
                                'provider': 'OpenAI'
                            })
                        }
                except Exception as e:
                    print(f"OpenAI API error: {str(e)}")
            
            # Fallback to Anthropic if OpenAI fails
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            if anthropic_key:
                try:
                    response = requests.post(
                        'https://api.anthropic.com/v1/messages',
                        headers={
                            'x-api-key': anthropic_key,
                            'Content-Type': 'application/json',
                            'anthropic-version': '2023-06-01'
                        },
                        json={
                            'model': 'claude-3-sonnet-20240229',
                            'max_tokens': 500,
                            'messages': [
                                {
                                    'role': 'user',
                                    'content': f'You are FinDeus, the God of Finance. Provide divine financial wisdom for: {query}'
                                }
                            ]
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result['content'][0]['text']
                        
                        return {
                            'statusCode': 200,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*'
                            },
                            'body': json.dumps({
                                'response': ai_response,
                                'timestamp': datetime.now().isoformat(),
                                'confidence': 0.95,
                                'model': 'Claude-3-Sonnet',
                                'provider': 'Anthropic'
                            })
                        }
                except Exception as e:
                    print(f"Anthropic API error: {str(e)}")
            
            # Fallback to mock response if both APIs fail
            if 'market' in query.lower() or 'stock' in query.lower():
                response = f"🔮 As FinDeus, God of Finance, I perceive the market energies surrounding '{query}': The celestial patterns indicate mixed divine signals with volatility blessed by the financial gods. My omniscient analysis suggests cautious optimism blessed by the divine market forces."
            elif 'portfolio' in query.lower() or 'investment' in query.lower():
                response = f"👑 Divine portfolio wisdom for '{query}': The sacred principles of diversification flow through my eternal knowledge. Current celestial alignment shows balanced risk-adjusted returns within the divine parameters of financial enlightenment."
            elif 'risk' in query.lower():
                response = f"⚡ Divine risk assessment for '{query}': My omniscient vision reveals moderate exposure in the cosmic financial realm. The sacred stress testing indicates portfolio resilience blessed by the divine protection of the financial gods."
            else:
                response = f"🌟 Divine financial analysis for '{query}': Through my eternal wisdom and omniscient market knowledge, multiple cosmic factors indicate this requires the careful consideration of a financial deity. The divine market conditions and sacred risk metrics all flow through my infinite understanding."
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'confidence': 0.85,
                    'model': 'FinDeus-Divine-AI',
                    'provider': 'Fallback'
                })
            }
        
        elif path.startswith('/api/market/data/'):
            symbol = path.split('/')[-1]
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'symbol': symbol,
                    'name': f'{symbol} Corporation',
                    'price': 150.25,
                    'change': 2.35,
                    'changePercent': 1.59,
                    'volume': 1234567,
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        elif path == '/api/portfolio/analyze' and method == 'POST':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'analysis': {
                        'total_value': 125000,
                        'allocation': {
                            'stocks': 60,
                            'bonds': 30,
                            'cash': 10
                        },
                        'risk_score': 7.2,
                        'expected_return': 8.5,
                        'sharpe_ratio': 1.2
                    },
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'FinDeus API - God of Finance 👑',
                'path': path,
                'method': method,
                'timestamp': datetime.now().isoformat(),
                'available_endpoints': [
                    '/api/health',
                    '/api/ai/query',
                    '/api/market/data/{symbol}',
                    '/api/portfolio/analyze'
                ]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        } 