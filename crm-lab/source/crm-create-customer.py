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
    Create a new customer.
    Required fields: name, email
    Optional fields: phone, company, position, status
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        required = ['name', 'email']
        for field in required:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'Required field missing: {field}'})
                }
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert new customer
        cursor.execute("""
            INSERT INTO customers (name, email, phone, company, position, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            body['name'],
            body['email'],
            body.get('phone'),
            body.get('company'),
            body.get('position'),
            body.get('status', 'active')
        ))
        
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
                'message': 'Customer created successfully',
                'id': result[0],
                'created_at': result[1].isoformat()
            })
        }
        
    except psycopg2.IntegrityError:
        return {
            'statusCode': 409,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Email already registered'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
