import json
import psycopg2
import os

def get_connection():
    """Establish database connection using environment variables."""
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=5432
    )

def lambda_handler(event, context):
    """
    Record a new interaction with a customer.
    Required fields: type
    Optional fields: description
    Path parameter: /customers/{id}/interactions
    """
    try:
        customer_id = event.get('pathParameters', {}).get('id')
        body = json.loads(event.get('body', '{}'))
        
        if not customer_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Customer ID not provided'})
            }
        
        if 'type' not in body:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Required field: type'})
            }
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify customer exists
        cursor.execute("SELECT id FROM customers WHERE id = %s", (customer_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Customer not found'})
            }
        
        # Insert interaction
        cursor.execute("""
            INSERT INTO interactions (customer_id, type, description)
            VALUES (%s, %s, %s)
            RETURNING id, interaction_date
        """, (customer_id, body['type'], body.get('description')))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Interaction recorded successfully',
                'interaction_id': result[0],
                'interaction_date': result[1].isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
