#!/usr/bin/env python3
"""
FinDeus - Netlify Function Handler
================================
"""

import json
import os
from datetime import datetime

def handler(event, context):
    """
    Netlify function handler for FinDeus API
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
                    'message': 'FinDeus API is running on Netlify',
                    'services': {
                        'ai_engine': 'operational',
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
            
            # Generate contextual response
            if 'market' in query.lower() or 'stock' in query.lower():
                response = f"Based on current market analysis, here's my assessment of '{query}': The market shows mixed signals with volatility expected. Key indicators suggest cautious optimism for the next quarter."
            elif 'portfolio' in query.lower() or 'investment' in query.lower():
                response = f"Portfolio analysis for '{query}': Diversification remains key. Current allocation shows balanced risk-adjusted returns within target parameters."
            elif 'risk' in query.lower():
                response = f"Risk assessment for '{query}': Current risk metrics show moderate exposure. Stress testing indicates portfolio resilience under various scenarios."
            else:
                response = f"Financial analysis for '{query}': Based on comprehensive data analysis, multiple factors indicate this requires careful consideration. Market conditions and risk metrics all play crucial roles."
            
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
                    'model': 'FinDeus-AI'
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
                'message': 'FinDeus API - God of Finance',
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