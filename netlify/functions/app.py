import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def handler(event, context):
    """
    Netlify serverless function handler for Flask app
    """
    try:
        # Import the Flask app here to avoid import issues
        from netlify_app import app
        
        # Get the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Remove the /.netlify/functions/app prefix if present
        if path.startswith('/.netlify/functions/app'):
            path = path[len('/.netlify/functions/app'):]
        if not path:
            path = '/'
            
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
            # Build query string
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            
            # Make the request
            response = client.open(
                path=path,
                method=http_method,
                headers=[(k, v) for k, v in headers.items()],
                query_string=query_string,
                data=body,
                content_type=headers.get('content-type', 'application/json')
            )
            
            # Get response headers
            response_headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
            
            # Add original response headers
            for key, value in response.headers:
                response_headers[key] = value
            
            # Return the response
            return {
                'statusCode': response.status_code,
                'headers': response_headers,
                'body': response.get_data(as_text=True),
                'isBase64Encoded': False
            }
            
    except ImportError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Import error',
                'message': str(e),
                'path': str(project_root)
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'type': type(e).__name__
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        } 