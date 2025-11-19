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
    List all customers with optional status filter.
    Query parameter: ?status=active
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        params = event.get('queryStringParameters') or {}
        status = params.get('status', None)
        
        # Build and execute query
        if status:
            cursor.execute(
                """SELECT id, name, email, phone, company, position, status, created_at 
                   FROM customers WHERE status = %s ORDER BY created_at DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT id, name, email, phone, company, position, status, created_at 
                   FROM customers ORDER BY created_at DESC"""
            )
        
        # Format results
        customers = []
        for row in cursor.fetchall():
            customers.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'company': row[4],
                'position': row[5],
                'status': row[6],
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'total': len(customers),
                'customers': customers
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
