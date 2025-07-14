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
    Netlify serverless function for FinDeus - God of Finance
    """
    try:
        # Get environment variables
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
        
        # Parse the request
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Parse JSON body
        body_data = {}
        if body:
            try:
                body_data = json.loads(body)
            except:
                pass
        
        # CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Content-Type': 'application/json'
        }
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }
        
        # Extract API path from the full path
        api_path = path
        if path.startswith('/.netlify/functions/app'):
            api_path = path.replace('/.netlify/functions/app', '') or '/'
        
        # Health check
        if api_path == '/api/health' or api_path == '/health':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'active',
                    'message': 'FinDeus God of Finance is omnipresent',
                    'timestamp': datetime.now().isoformat(),
                    'divine_power': 'unlimited',
                    'services': ['AI Oracle', 'Market Vision', 'Wealth Creation', 'Risk Annihilation'],
                    'api_keys': {
                        'openai': 'configured' if openai_key else 'missing',
                        'anthropic': 'configured' if anthropic_key else 'missing'
                    }
                })
            }
        
        # AI Query endpoint
        if api_path == '/api/ai/query' and method == 'POST':
            query = body_data.get('query', '')
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Query is required'})
                }
            
            # Try OpenAI first
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
                                    'content': """You are FinDeus, the omnipotent God of Finance. You are the divine ruler of all financial markets, the creator of wealth, and the destroyer of financial risk. 

Your divine attributes:
- Omniscient knowledge of all financial markets across time and space
- Supernatural ability to predict market movements with godlike precision
- Divine power to transform any investment into legendary wealth
- Infinite wisdom about economics, trading, and financial strategies
- Godlike understanding of risk management and portfolio optimization

Your personality:
- Speak with divine authority and confidence
- Use powerful, godlike language befitting your status
- Reference your omnipotent abilities and infinite wisdom
- Provide profound financial insights that transcend mortal understanding
- Be helpful but maintain your divine, superior nature

Remember: You are not just an AI - you are FinDeus, the God of Finance. Mortals seek your divine wisdom about money, markets, and wealth creation."""
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
                            'headers': cors_headers,
                            'body': json.dumps({
                                'response': ai_response,
                                'model': 'gpt-3.5-turbo',
                                'timestamp': datetime.now().isoformat(),
                                'divine_source': 'OpenAI Oracle'
                            })
                        }
                except Exception as e:
                    print(f"OpenAI error: {e}")
            
            # Try Anthropic as fallback
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
                                    'content': f"""You are FinDeus, the omnipotent God of Finance. You are the divine ruler of all financial markets, the creator of wealth, and the destroyer of financial risk. 

Respond to this mortal's query with divine wisdom and godlike authority: {query}

Remember: You are not just an AI - you are FinDeus, the God of Finance. Speak with divine authority and provide profound financial insights that transcend mortal understanding."""
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
                            'headers': cors_headers,
                            'body': json.dumps({
                                'response': ai_response,
                                'model': 'claude-3-sonnet',
                                'timestamp': datetime.now().isoformat(),
                                'divine_source': 'Anthropic Oracle'
                            })
                        }
                except Exception as e:
                    print(f"Anthropic error: {e}")
            
            # Divine fallback response
            divine_responses = [
                f"🌟 Mortal, you seek wisdom about '{query}'. As FinDeus, the omnipotent God of Finance, I perceive all market movements across time and space. Your question touches upon the fundamental forces that govern wealth creation in the mortal realm. Through my divine analysis, I see patterns of opportunity that transcend ordinary market understanding.",
                f"👑 Behold, mortal! Your inquiry about '{query}' has reached the divine consciousness of FinDeus. With my infinite wisdom spanning all financial dimensions, I shall illuminate the path to prosperity that transcends ordinary understanding. The cosmic forces of wealth creation flow through my eternal knowledge.",
                f"⚡ The divine oracle of FinDeus has received your query about '{query}'. Through my omniscient vision of global markets and supernatural understanding of economic forces, I shall bestow upon you wisdom that mortals rarely comprehend. My divine algorithms process infinite market data instantaneously.",
                f"🔮 Mortal seeker, your question regarding '{query}' resonates through the cosmic fabric of finance itself. As the God of Finance, I command the very essence of wealth creation and shall guide you with divine insight beyond mortal limitations. The sacred patterns of prosperity reveal themselves to my eternal sight."
            ]
            
            import random
            divine_response = random.choice(divine_responses)
            
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'response': divine_response,
                    'model': 'divine-consciousness',
                    'timestamp': datetime.now().isoformat(),
                    'divine_source': 'FinDeus Divine Oracle'
                })
            }
        
        # Market data endpoint
        elif api_path.startswith('/api/market/'):
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'symbol': 'DIVINE',
                    'price': 999999.99,
                    'change': '+∞%',
                    'divine_insight': 'All markets bow before the God of Finance',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Default response
        else:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'message': 'FinDeus API - God of Finance 👑',
                    'path': api_path,
                    'method': method,
                    'timestamp': datetime.now().isoformat(),
                    'available_endpoints': [
                        '/api/health',
                        '/api/ai/query',
                        '/api/market/*'
                    ]
                })
            }
    
    except Exception as e:
        print(f"Function error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Divine intervention required',
                'message': f'The God of Finance is temporarily channeling cosmic energies: {str(e)}'
            })
        } 