import json
import psycopg2
import boto3
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
    Delete a customer and all associated data.
    Also removes files from S3.
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
        
        # Get document S3 keys before deletion
        cursor.execute("SELECT s3_key FROM documents WHERE customer_id = %s", (customer_id,))
        documents = cursor.fetchall()
        
        # Delete files from S3
        if documents:
            s3 = boto3.client('s3')
            bucket = os.environ['S3_BUCKET']
            for doc in documents:
                try:
                    s3.delete_object(Bucket=bucket, Key=doc[0])
                except Exception:
                    pass  # Continue even if S3 deletion fails
        
        # Delete customer (CASCADE will delete interactions and documents)
        cursor.execute("DELETE FROM customers WHERE id = %s RETURNING id", (customer_id,))
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
                'message': 'Customer deleted successfully',
                'id': result[0]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
