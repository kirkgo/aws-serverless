import json
import psycopg2
import os
from datetime import datetime

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
    Update customer information.
    Path parameter: /customers/{id}
    Allowed fields: name, email, phone, company, position, status
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
        
        # Define allowed fields for update
        allowed_fields = ['name', 'email', 'phone', 'company', 'position', 'status']
        updates = []
        values = []
        
        # Build dynamic update query
        for field in allowed_fields:
            if field in body:
                updates.append(f"{field} = %s")
                values.append(body[field])
        
        if not updates:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No fields to update'})
            }
        
        # Add updated_at timestamp
        updates.append("updated_at = %s")
        values.append(datetime.now())
        values.append(customer_id)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = f"UPDATE customers SET {', '.join(updates)} WHERE id = %s RETURNING id"
        cursor.execute(query, values)
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Customer not found'})
            }
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Customer updated successfully',
                'id': result[0]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
