#!/usr/bin/env python3
"""
FinDeus - Netlify Function Handler
================================
"""

import json
import os
import sys
from pathlib import Path

# Add the root directory to the Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from web_app import app
except ImportError:
    # Fallback if import fails
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({'message': 'FinDeus API is running on Netlify'})

def handler(event, context):
    """
    Netlify function handler for Flask app
    """
    try:
        # Get request details from event
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Convert query string to proper format
        query_params = []
        for key, value in query_string.items():
            query_params.append(f"{key}={value}")
        query_string_formatted = '&'.join(query_params)
        
        # Create test client and make request
        with app.test_client() as client:
            response = client.open(
                path=path,
                method=method,
                data=body,
                headers=headers,
                query_string=query_string_formatted
            )
            
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': response.content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': response.get_data(as_text=True)
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
                'message': str(e)
            })
        } 