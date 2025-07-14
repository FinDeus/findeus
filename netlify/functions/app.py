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
        # Import Flask app
        from netlify_app import app
        
        # Get request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Handle base64 encoded body
        if body and event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Remove function prefix from path
        if path.startswith('/.netlify/functions/app'):
            path = path[len('/.netlify/functions/app'):]
        if not path:
            path = '/'
        
        # Create Flask test client
        with app.test_client() as client:
            # Build query string
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else ''
            
            # Make request to Flask app
            response = client.open(
                path=path,
                method=http_method,
                headers=list(headers.items()),
                query_string=query_string,
                data=body,
                content_type=headers.get('content-type', 'application/json')
            )
            
            # Prepare response headers
            response_headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
            
            # Add Flask response headers
            for key, value in response.headers:
                response_headers[key] = value
            
            return {
                'statusCode': response.status_code,
                'headers': response_headers,
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        # Return detailed error for debugging
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Function execution failed',
                'message': str(e),
                'type': type(e).__name__,
                'path': path if 'path' in locals() else 'unknown',
                'method': http_method if 'http_method' in locals() else 'unknown'
            })
        } 