import json
import psycopg2
import boto3
import base64
import os
import uuid

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
    Upload a document for a customer.
    Required fields: file (base64), filename
    Optional fields: file_type
    Path parameter: /customers/{id}/documents
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
        
        # Validate required fields
        if 'file' not in body or 'filename' not in body:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Required fields: file (base64), filename'})
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
        
        # Decode base64 file
        file_bytes = base64.b64decode(body['file'])
        filename = body['filename']
        file_type = body.get('file_type', 'application/octet-stream')
        
        # Generate unique S3 key
        file_id = str(uuid.uuid4())
        s3_key = f"customers/{customer_id}/{file_id}_{filename}"
        
        # Upload to S3
        s3 = boto3.client('s3')
        bucket = os.environ['S3_BUCKET']
        
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=file_bytes,
            ContentType=file_type
        )
        
        # Save document metadata to database
        cursor.execute("""
            INSERT INTO documents (customer_id, filename, s3_key, file_type, size_bytes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, uploaded_at
        """, (customer_id, filename, s3_key, file_type, len(file_bytes)))
        
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
                'message': 'Document uploaded successfully',
                'document_id': result[0],
                's3_key': s3_key,
                'uploaded_at': result[1].isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
