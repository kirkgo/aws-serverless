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
    Get customer details by ID, including interactions and documents.
    Path parameter: /customers/{id}
    """
    try:
        customer_id = event.get('pathParameters', {}).get('id')
        
        if not customer_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Customer ID not provided'})
            }
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get customer details
        cursor.execute("""
            SELECT id, name, email, phone, company, position, status, created_at, updated_at
            FROM customers WHERE id = %s
        """, (customer_id,))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Customer not found'})
            }
        
        customer = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'company': row[4],
            'position': row[5],
            'status': row[6],
            'created_at': row[7].isoformat() if row[7] else None,
            'updated_at': row[8].isoformat() if row[8] else None
        }
        
        # Get customer interactions
        cursor.execute("""
            SELECT id, type, description, interaction_date
            FROM interactions WHERE customer_id = %s
            ORDER BY interaction_date DESC
        """, (customer_id,))
        
        customer['interactions'] = [{
            'id': r[0],
            'type': r[1],
            'description': r[2],
            'date': r[3].isoformat() if r[3] else None
        } for r in cursor.fetchall()]
        
        # Get customer documents
        cursor.execute("""
            SELECT id, filename, s3_key, file_type, uploaded_at
            FROM documents WHERE customer_id = %s
            ORDER BY uploaded_at DESC
        """, (customer_id,))
        
        customer['documents'] = [{
            'id': r[0],
            'filename': r[1],
            's3_key': r[2],
            'file_type': r[3],
            'uploaded_at': r[4].isoformat() if r[4] else None
        } for r in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(customer)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
