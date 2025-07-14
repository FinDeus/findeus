import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the Flask app
from netlify_app import app

def handler(event, context):
    """
    Netlify serverless function handler for Flask app
    """
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Get headers
        headers = event.get('headers', {})
        
        # Get body
        body = event.get('body', '')
        if body and event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Create a test client
        with app.test_client() as client:
            # Make the request
            response = client.open(
                path=path,
                method=http_method,
                headers=headers,
                query_string=query_params,
                data=body
            )
            
            # Return the response
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True),
                'isBase64Encoded': False
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        } 