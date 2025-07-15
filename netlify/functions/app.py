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
    Netlify serverless function for FinDeus AI - God of Finance
    """
    try:
        # Get environment variables
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Parse the request
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '')
        
        # Determine the route - check query params first, then path
        if 'path' in query_params:
            api_path = query_params['path']
            route = f'/api/{api_path}'
        else:
            # Extract from path (for direct function calls)
            if path.startswith('/.netlify/functions/app'):
                # Extract the API path from the URL
                path_parts = path.split('/')
                if len(path_parts) > 4:
                    route = f'/api/{"/".join(path_parts[4:])}'
                else:
                    route = '/api/health'  # default
            else:
                route = path
        
        # Parse JSON body
        body_data = {}
        if body:
            try:
                body_data = json.loads(body)
            except:
                pass
        
        # Route handling
        if route == '/api/health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'FinDeus - Financial Intelligence',
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'openai_configured': bool(openai_key)
                })
            }
        
        elif route == '/api/ai/query' and method == 'POST':
            query = body_data.get('query', '')
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query is required'})
                }
            
            # Call OpenAI API
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
                                    'content': 'You are FinDeus, a highly knowledgeable financial AI assistant. You provide expert financial advice, market analysis, and investment guidance with professional authority. Always give practical, actionable advice while maintaining a professional tone.'
                                },
                                {
                                    'role': 'user',
                                    'content': query
                                }
                            ],
                            'max_tokens': 1000,
                            'temperature': 0.7
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result['choices'][0]['message']['content']
                        
                        return {
                            'statusCode': 200,
                            'headers': headers,
                            'body': json.dumps({
                                'response': ai_response,
                                'timestamp': datetime.now().isoformat(),
                                'model': 'gpt-3.5-turbo',
                                'service': 'FinDeus Financial Intelligence'
                            })
                        }
                    else:
                        return {
                            'statusCode': 200,
                            'headers': headers,
                            'body': json.dumps({
                                'response': f'I understand you\'re asking about "{query}". While I\'m experiencing some technical difficulties, I can provide general financial guidance. For specific investment advice, I recommend consulting with a qualified financial advisor.',
                                'timestamp': datetime.now().isoformat(),
                                'model': 'fallback',
                                'service': 'FinDeus Financial Intelligence'
                            })
                        }
                        
                except Exception as e:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({
                            'response': f'Thank you for your question about "{query}". I\'m currently experiencing some technical issues, but I can offer this general advice: Always diversify your investments, understand your risk tolerance, and consider consulting with a financial professional.',
                            'timestamp': datetime.now().isoformat(),
                            'model': 'fallback',
                            'service': 'FinDeus Financial Intelligence'
                        })
                    }
            else:
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'response': f'I appreciate your question about "{query}". While I\'m currently operating in limited mode, I can provide general financial guidance: Focus on building an emergency fund, diversify your investments, understand your risk tolerance, and consider long-term investment strategies.',
                        'timestamp': datetime.now().isoformat(),
                        'model': 'general-guidance',
                        'service': 'FinDeus Financial Intelligence'
                    })
                }
        
        # Default response for unhandled routes
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'error': 'Route not found',
                'route': route,
                'method': method,
                'available_routes': ['/api/health', '/api/ai/query'],
                'debug': {
                    'path': path,
                    'query_params': query_params
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        } 