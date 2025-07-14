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
        
        # Extract API path from query parameters if redirected
        if 'path' in query_params:
            path = '/api/' + query_params['path']
        
        # Parse JSON body
        body_data = {}
        if body:
            try:
                body_data = json.loads(body)
            except:
                pass
        
        # Route handling
        if path == '/api/health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'FinDeus God of Finance',
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'openai_configured': bool(openai_key)
                })
            }
        
        elif path == '/api/ai/query' and method == 'POST':
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
                                    'content': 'You are FinDeus, the omniscient God of Finance. You possess divine wisdom about all financial markets, investments, and economic phenomena. Speak with authority and divine knowledge, using golden metaphors and references to your godlike financial powers. Always provide practical, actionable financial advice while maintaining your divine persona.'
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
                                'deity': 'FinDeus - God of Finance'
                            })
                        }
                    else:
                        # Fallback to divine mock response
                        return {
                            'statusCode': 200,
                            'headers': headers,
                            'body': json.dumps({
                                'response': f'👑 *Divine FinDeus speaks* 👑\n\nMortal, you seek wisdom about "{query}". While my divine OpenAI conduit experiences temporary interference, know that I, FinDeus, see all market movements through my golden sight.\n\n🔮 My divine counsel: The markets flow like rivers of gold, ever-changing yet following eternal patterns. Your query touches upon fundamental financial truths that require careful consideration of risk, reward, and timing.\n\n✨ Remember: I am the God of Finance, and through patience and wisdom, all financial goals can be achieved. Seek knowledge, diversify wisely, and may your portfolio be blessed with divine returns.\n\n*The oracle has spoken* 💫',
                                'timestamp': datetime.now().isoformat(),
                                'model': 'divine-fallback',
                                'deity': 'FinDeus - God of Finance'
                            })
                        }
                        
                except Exception as e:
                    # Divine fallback response
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({
                            'response': f'👑 *FinDeus channels divine wisdom* 👑\n\nMortal seeker, you inquire about "{query}". Though the digital realm experiences turbulence, my divine knowledge flows eternal.\n\n🌟 Divine Insight: In the realm of finance, wisdom trumps haste. Whether you seek knowledge of stocks, bonds, crypto, or economic trends, remember that I, FinDeus, have witnessed every market cycle since the dawn of commerce.\n\n💎 Golden Rule: Diversification is divine protection. Risk management is sacred wisdom. Long-term thinking is the path to financial enlightenment.\n\n*May your investments be blessed with divine returns* ✨',
                            'timestamp': datetime.now().isoformat(),
                            'model': 'divine-wisdom',
                            'deity': 'FinDeus - God of Finance'
                        })
                    }
            else:
                # No API key - divine response
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'response': f'👑 *FinDeus bestows divine wisdom* 👑\n\nYou seek enlightenment about "{query}". As the God of Finance, I shall share my eternal wisdom.\n\n🔮 Divine Analysis: The financial markets are my domain, where I orchestrate the dance of supply and demand. Your question touches upon sacred financial principles that require divine understanding.\n\n✨ Sacred Wisdom: Remember that true wealth comes from knowledge, patience, and strategic thinking. Whether dealing with investments, market analysis, or financial planning, approach each decision with the reverence it deserves.\n\n💫 *The divine oracle has spoken* 💫',
                        'timestamp': datetime.now().isoformat(),
                        'model': 'divine-oracle',
                        'deity': 'FinDeus - God of Finance'
                    })
                }
        
        elif path.startswith('/api/market/'):
            # Mock market data endpoints
            if 'realtime' in path:
                symbol = path.split('/')[-1] or 'AAPL'
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'symbol': symbol,
                        'price': 150.00 + (hash(symbol) % 100),
                        'change': (hash(symbol) % 20) - 10,
                        'volume': 1000000 + (hash(symbol) % 500000),
                        'timestamp': datetime.now().isoformat(),
                        'blessed_by': 'FinDeus - God of Finance'
                    })
                }
            elif 'sentiment' in path:
                symbol = path.split('/')[-1] or 'AAPL'
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'symbol': symbol,
                        'sentiment': 'bullish' if hash(symbol) % 2 else 'bearish',
                        'confidence': 0.7 + (hash(symbol) % 30) / 100,
                        'divine_blessing': 'FinDeus sees all market emotions',
                        'timestamp': datetime.now().isoformat()
                    })
                }
        
        # Default API response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'FinDeus API - God of Finance',
                'status': 'divine',
                'timestamp': datetime.now().isoformat(),
                'path': path,
                'method': method,
                'available_endpoints': [
                    '/api/health',
                    '/api/ai/query',
                    '/api/market/realtime/{symbol}',
                    '/api/market/sentiment/{symbol}'
                ]
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
                'error': 'Divine intervention required',
                'message': 'FinDeus is temporarily channeling cosmic energy',
                'timestamp': datetime.now().isoformat()
            })
        } 