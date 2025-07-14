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

from web_app import app

def handler(event, context):
    """
    Netlify function handler for Flask app
    """
    try:
        # Import the WSGI adapter
        from werkzeug.serving import WSGIRequestHandler
        from werkzeug.wrappers import Request, Response
        
        # Create a request object from the event
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Handle the request with Flask
        with app.test_request_context(
            path=path,
            method=method,
            query_string=query_string,
            headers=headers,
            data=body
        ):
            response = app.full_dispatch_request()
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        } 