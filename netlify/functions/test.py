import json

def handler(event, context):
    """
    Simple test function to verify Netlify functions are working
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Netlify function is working!',
            'event': event,
            'context': context.__dict__ if hasattr(context, '__dict__') else str(context)
        })
    } 