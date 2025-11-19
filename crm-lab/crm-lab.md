# Lab: Building a CRM with AWS Lambda, API Gateway, RDS Postgres, and S3

## Lab Overview

**Duration:** 1-2 hours  
**Level:** Intermediate  
**Cost:** Approximately $0 (Free Tier eligible)

### Objectives

By the end of this lab, you will be able to:
- Create and configure an RDS PostgreSQL database
- Set up S3 buckets for file storage
- Develop Lambda functions for serverless computing
- Build a REST API using API Gateway
- Integrate all components into a functional CRM system

### Architecture Overview

```
Client → API Gateway → Lambda → RDS Postgres → S3 (files)
```

### What You Will Build

- **RDS Postgres**: Database to store customer information
- **S3**: Storage for customer documents
- **Lambda**: Serverless functions for CRUD operations
- **API Gateway**: REST API to expose the functions


## Part 1: Configure VPC and Security Groups

### Introduction

Security Groups act as virtual firewalls for your AWS resources. In this section, you'll create two security groups: one for the RDS database and another for the Lambda functions. This ensures that only authorized traffic can reach your resources.

### Step 1.1: Create Security Group for RDS

**Why this step?** The RDS security group controls which IP addresses and resources can connect to your database on port 5432 (PostgreSQL default port).

1. Navigate to **AWS Console** → **VPC** → **Security Groups**
2. Click **Create security group**
3. Configure the following settings:
   - **Security group name**: `crm-rds-sg`
   - **Description**: `Security group for CRM RDS database`
   - **VPC**: Select the default VPC
4. In **Inbound rules**, click **Add rule**:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Anywhere-IPv4 (0.0.0.0/0)
   
   > **Note**: Opening to 0.0.0.0/0 is only for lab purposes. In production, restrict this to specific IP ranges.

5. Click **Create security group**

**Expected Result**: Security group `crm-rds-sg` created successfully.

### Step 1.2: Create Security Group for Lambda

**Why this step?** Lambda functions running inside a VPC need a security group to control their outbound traffic to other resources like RDS.

1. Click **Create security group**
2. Configure the following settings:
   - **Security group name**: `crm-lambda-sg`
   - **Description**: `Security group for CRM Lambda functions`
   - **VPC**: Select the default VPC
3. In **Outbound rules**, keep the default rule (All traffic)
   
   > **Info**: Lambda needs outbound access to reach RDS and S3 services.

4. Click **Create security group**

**Expected Result**: Security group `crm-lambda-sg` created successfully.

## Part 2: Create the RDS PostgreSQL Database

### Introduction

Amazon RDS (Relational Database Service) makes it easy to set up, operate, and scale a relational database in the cloud. In this section, you'll create a PostgreSQL instance that will store all your CRM data.

### Step 2.1: Create the RDS Instance

**Why this step?** The database is the core of your CRM, storing all customer information, interactions, and document metadata.

1. Navigate to **AWS Console** → **RDS** → **Databases**
2. Click **Create database**
3. Configure the following settings:

**Creation method:**
- Select **Standard create**

**Engine options:**
- **Engine type**: PostgreSQL
- **Version**: PostgreSQL 15.x (or latest available)

**Templates:**
- Select **Free tier**

   > **Tip**: Free tier includes 750 hours of db.t3.micro usage per month.

**Settings:**
- **DB instance identifier**: `crm-database`
- **Master username**: `crmadmin`
- **Master password**: `CrmLab2025!`

   > **Important**: Save these credentials securely. You'll need them for Lambda configuration.

**Instance configuration:**
- **DB instance class**: db.t3.micro

**Storage:**
- **Storage type**: gp2
- **Allocated storage**: 20 GB
- Uncheck **Enable storage autoscaling**

**Connectivity:**
- **VPC**: Default VPC
- **Public access**: Yes
- **VPC security group**: Select **Choose existing**
- Remove the default security group and add `crm-rds-sg`

**Database authentication:**
- Select **Password authentication**

**Additional configuration:**
- **Initial database name**: `crmdb`
- Uncheck **Enable automated backups** (to save costs during the lab)
- Uncheck **Enable Enhanced monitoring**

4. Click **Create database**
5. Wait approximately 10 minutes until the status changes to **Available**

**Expected Result**: RDS instance `crm-database` is running and available.

### Step 2.2: Record the RDS Endpoint

**Why this step?** The endpoint is the address your Lambda functions will use to connect to the database.

1. Click on the database `crm-database`
2. In the **Connectivity & security** tab, copy the **Endpoint**
   - Example: `crm-database.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com`
3. Save this endpoint for later use in Lambda configuration

**Expected Result**: You have recorded the RDS endpoint address.

### Step 2.3: Create the CRM Database Tables

**Why this step?** You need to create the table structure that will hold your CRM data: customers, interactions, and documents.

1. Connect to the database using a PostgreSQL client (DBeaver, pgAdmin, or AWS CloudShell with psql)
2. Execute the following SQL script:

```sql
-- Customers table: stores main customer information
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(100),
    position VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interactions table: tracks all customer interactions
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table: metadata for files stored in S3
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    size_bytes BIGINT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_interactions_customer ON interactions(customer_id);
CREATE INDEX idx_documents_customer ON documents(customer_id);
```

   > **Info**: The CASCADE option ensures that when a customer is deleted, all related interactions and documents are also removed.

**Expected Result**: Three tables (customers, interactions, documents) created with appropriate indexes.


## Part 3: Create the S3 Bucket

### Introduction

Amazon S3 (Simple Storage Service) provides object storage for your customer documents. In this section, you'll create a bucket to store files like contracts, proposals, and other customer-related documents.

### Step 3.1: Create the Bucket

**Why this step?** S3 provides durable, scalable storage for customer documents that would be too large to store in the database.

1. Navigate to **AWS Console** → **S3**
2. Click **Create bucket**
3. Configure the following settings:
   - **Bucket name**: `crm-documents-[your-unique-id]` (e.g., crm-documents-12345)
   
   > **Note**: Bucket names must be globally unique across all AWS accounts.
   
   - **Region**: Same region as your RDS instance
   - **Object Ownership**: ACLs disabled
   - **Block Public Access**: Keep all options checked
   - **Bucket Versioning**: Disable
4. Click **Create bucket**

**Expected Result**: S3 bucket created successfully.

### Step 3.2: Create Folder Structure

**Why this step?** Organizing files in folders makes it easier to manage documents by customer.

1. Enter the bucket you created
2. Click **Create folder**
3. Create the folder: `customers/`
4. Click **Create folder**

**Expected Result**: Folder structure `customers/` created inside the bucket.

## Part 4: Create the IAM Role for Lambda

### Introduction

IAM (Identity and Access Management) roles define what permissions your Lambda functions have. In this section, you'll create a role that allows Lambda to access RDS, S3, CloudWatch Logs, and VPC networking.

### Step 4.1: Create Custom Policy

**Why this step?** A custom policy gives you fine-grained control over exactly what resources your Lambda functions can access.

1. Navigate to **AWS Console** → **IAM** → **Policies**
2. Click **Create policy**
3. Select the **JSON** tab and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::crm-documents-*",
                "arn:aws:s3:::crm-documents-*/*"
            ]
        },
        {
            "Sid": "VPCAccess",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
                "ec2:AssignPrivateIpAddresses",
                "ec2:UnassignPrivateIpAddresses"
            ],
            "Resource": "*"
        }
    ]
}
```

   > **Info**: Each "Sid" identifies a different set of permissions: logging, S3 access, and VPC networking.

4. Click **Next**
5. **Policy name**: `CRM-Lambda-Policy`
6. Click **Create policy**

**Expected Result**: Policy `CRM-Lambda-Policy` created successfully.

### Step 4.2: Create the IAM Role

**Why this step?** The role is what you'll attach to your Lambda functions, giving them the permissions defined in the policy.

1. Navigate to **IAM** → **Roles**
2. Click **Create role**
3. Configure:
   - **Trusted entity type**: AWS service
   - **Use case**: Lambda
4. Click **Next**
5. Search for and select:
   - `CRM-Lambda-Policy` (the policy you just created)
6. Click **Next**
7. **Role name**: `CRM-Lambda-Role`
8. Click **Create role**

**Expected Result**: Role `CRM-Lambda-Role` created with the custom policy attached.

## Part 5: Create the Lambda Functions

### Introduction

AWS Lambda lets you run code without provisioning or managing servers. In this section, you'll create seven Lambda functions that handle all CRM operations: listing, creating, reading, updating, and deleting customers, plus managing documents and interactions.

### Step 5.1: Create Lambda Layer with Dependencies

**Why this step?** Lambda layers allow you to package libraries (like the PostgreSQL driver) separately from your function code, making it reusable across multiple functions.

**On your local computer:**

1. Create a directory and install the PostgreSQL driver:

```bash
mkdir -p python
pip install psycopg2-binary -t python/
zip -r psycopg2-layer.zip python
```

**In AWS Console:**

2. Navigate to **AWS Console** → **Lambda** → **Layers**
3. Click **Create layer**
4. Configure:
   - **Name**: `psycopg2-layer`
   - **Upload**: Select the `psycopg2-layer.zip` file
   - **Compatible runtimes**: Python 3.11
5. Click **Create**

**Expected Result**: Layer `psycopg2-layer` created and ready to use.

---

### Step 5.2: Create Function - List Customers

**Why this step?** This function retrieves all customers from the database, with optional filtering by status.

1. Navigate to **Lambda** → **Functions** → **Create function**
2. Configure:
   - **Function name**: `crm-list-customers`
   - **Runtime**: Python 3.11
   - **Architecture**: x86_64
   - **Execution role**: Use an existing role → `CRM-Lambda-Role`
3. Click **Create function**

4. In the **Code** tab, replace the default code with:

```python
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
```

5. Click **Deploy**

6. Configure **Environment Variables** (Configuration → Environment variables):
   - `DB_HOST`: [your RDS endpoint]
   - `DB_NAME`: crmdb
   - `DB_USER`: crmadmin
   - `DB_PASSWORD`: CrmLab2025!

7. Configure **General Configuration** (Configuration → General configuration):
   - **Timeout**: 30 seconds
   - **Memory**: 256 MB

8. Configure **VPC** (Configuration → VPC):
   - Select the default VPC
   - Select at least 2 subnets
   - Security group: `crm-lambda-sg`

9. Add **Layer** (scroll down to Layers → Add a layer):
   - Select **Custom layers**
   - Choose `psycopg2-layer`
   - Click **Add**

**Expected Result**: Function `crm-list-customers` deployed and configured.

---

### Step 5.3: Create Function - Create Customer

**Why this step?** This function allows adding new customers to the CRM database.

1. Create a new function: `crm-create-customer`
2. Use the same configuration as the previous function
3. Replace the code with:

```python
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
```

4. Configure the same environment variables, VPC, and layer as the previous function

**Expected Result**: Function `crm-create-customer` deployed and configured.

---

### Step 5.4: Create Function - Get Customer by ID

**Why this step?** This function retrieves detailed information about a specific customer, including their interactions and documents.

1. Create a new function: `crm-get-customer`
2. Replace the code with:

```python
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
```

3. Configure environment variables, VPC, and layer

**Expected Result**: Function `crm-get-customer` deployed and configured.

---

### Step 5.5: Create Function - Update Customer

**Why this step?** This function allows updating existing customer information.

1. Create a new function: `crm-update-customer`
2. Replace the code with:

```python
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
```

3. Configure environment variables, VPC, and layer

**Expected Result**: Function `crm-update-customer` deployed and configured.

---

### Step 5.6: Create Function - Delete Customer

**Why this step?** This function removes a customer and all associated data (interactions and documents) from the system.

1. Create a new function: `crm-delete-customer`
2. Replace the code with:

```python
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
```

3. Configure environment variables, VPC, and layer
4. Add an additional environment variable:
   - `S3_BUCKET`: [your bucket name]

**Expected Result**: Function `crm-delete-customer` deployed and configured.

---

### Step 5.7: Create Function - Upload Document

**Why this step?** This function allows uploading documents (contracts, proposals, etc.) associated with a customer.

1. Create a new function: `crm-upload-document`
2. Replace the code with:

```python
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
```

3. Configure environment variables (including `S3_BUCKET`), VPC, and layer

**Expected Result**: Function `crm-upload-document` deployed and configured.

---

### Step 5.8: Create Function - Record Interaction

**Why this step?** This function tracks all interactions with customers (emails, calls, meetings, etc.).

1. Create a new function: `crm-record-interaction`
2. Replace the code with:

```python
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
```

3. Configure environment variables, VPC, and layer

**Expected Result**: Function `crm-record-interaction` deployed and configured.

---

## Part 6: Create the API Gateway

### Introduction

Amazon API Gateway is a fully managed service that makes it easy to create, publish, and maintain APIs. In this section, you'll create a REST API that exposes your Lambda functions as HTTP endpoints.

### Step 6.1: Create the REST API

**Why this step?** The API Gateway acts as the front door for your CRM, receiving HTTP requests and routing them to the appropriate Lambda function.

1. Navigate to **AWS Console** → **API Gateway**
2. Click **Create API**
3. In **REST API**, click **Build**
4. Configure:
   - **Protocol**: REST
   - **Create new API**: New API
   - **API name**: `CRM-API`
   - **Endpoint Type**: Regional
5. Click **Create API**

**Expected Result**: REST API `CRM-API` created.

### Step 6.2: Create Resource /customers

**Why this step?** Resources define the URL structure of your API. The `/customers` resource will be the base path for all customer operations.

1. Click **Create resource**
2. Configure:
   - **Resource name**: `customers`
   - **Resource path**: `/customers`
   - Check **CORS (Cross Origin Resource Sharing)**
   
   > **Info**: CORS allows your API to be called from web browsers on different domains.

3. Click **Create resource**

**Expected Result**: Resource `/customers` created with CORS enabled.

### Step 6.3: Create Methods for /customers

**Why this step?** Methods define the HTTP verbs (GET, POST, etc.) that your API accepts and link them to Lambda functions.

**GET - List Customers:**

1. Select the `/customers` resource
2. Click **Create method**
3. Configure:
   - **Method type**: GET
   - **Integration type**: Lambda Function
   - **Lambda function**: `crm-list-customers`
4. Click **Create method**

**POST - Create Customer:**

1. Click **Create method**
2. Configure:
   - **Method type**: POST
   - **Integration type**: Lambda Function
   - **Lambda function**: `crm-create-customer`
3. Click **Create method**

**Expected Result**: GET and POST methods created for `/customers`.

### Step 6.4: Create Resource /customers/{id}

**Why this step?** The `{id}` path parameter allows you to specify which customer you want to operate on.

1. Select `/customers`
2. Click **Create resource**
3. Configure:
   - **Resource name**: `{id}`
   - **Resource path**: `{id}`
   - Check **CORS**
4. Click **Create resource**

**Expected Result**: Resource `/customers/{id}` created.

### Step 6.5: Create Methods for /customers/{id}

**GET - Get Customer:**
1. Select `/customers/{id}`
2. Create GET method → Lambda: `crm-get-customer`

**PUT - Update Customer:**
1. Create PUT method → Lambda: `crm-update-customer`

**DELETE - Delete Customer:**
1. Create DELETE method → Lambda: `crm-delete-customer`

**Expected Result**: GET, PUT, and DELETE methods created for `/customers/{id}`.

### Step 6.6: Create Resource /customers/{id}/documents

**Why this step?** This nested resource allows uploading documents associated with a specific customer.

1. Select `/customers/{id}`
2. Click **Create resource**
3. Configure:
   - **Resource name**: `documents`
   - Check **CORS**
4. Click **Create resource**
5. Create POST method → Lambda: `crm-upload-document`

**Expected Result**: POST method created for `/customers/{id}/documents`.

### Step 6.7: Create Resource /customers/{id}/interactions

**Why this step?** This nested resource allows recording interactions with a specific customer.

1. Select `/customers/{id}`
2. Click **Create resource**
3. Configure:
   - **Resource name**: `interactions`
   - Check **CORS**
4. Click **Create resource**
5. Create POST method → Lambda: `crm-record-interaction`

**Expected Result**: POST method created for `/customers/{id}/interactions`.

### Step 6.8: Deploy the API

**Why this step?** Deploying creates a publicly accessible URL for your API.

1. Click **Deploy API**
2. Configure:
   - **Stage**: New Stage
   - **Stage name**: `prod`
3. Click **Deploy**
4. Copy the **Invoke URL** (e.g., `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod`)

   > **Important**: Save this URL. You'll use it to test your API.

**Expected Result**: API deployed to the `prod` stage with a public URL.

---

## Part 7: Test the API

### Introduction

Now it's time to test your CRM API. You'll use curl commands to verify each endpoint works correctly. You can also use tools like Postman or Insomnia.

### Step 7.1: Create a Customer

**Why this step?** Verify that you can add new customers to the system.

```bash
curl -X POST https://[your-api-url]/prod/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Silva",
    "email": "maria@empresa.pt",
    "phone": "+351 912 345 678",
    "company": "Tech Corp",
    "position": "IT Manager"
  }'
```

**Expected Response:**
```json
{
  "message": "Customer created successfully",
  "id": 1,
  "created_at": "2024-01-15T10:30:00"
}
```

### Step 7.2: List Customers

**Why this step?** Verify that you can retrieve all customers.

```bash
curl https://[your-api-url]/prod/customers
```

**Expected Response:**
```json
{
  "total": 1,
  "customers": [
    {
      "id": 1,
      "name": "Maria Silva",
      "email": "maria@empresa.pt",
      "phone": "+351 912 345 678",
      "company": "Tech Corp",
      "position": "IT Manager",
      "status": "active",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Step 7.3: Get Customer by ID

**Why this step?** Verify that you can retrieve detailed information about a specific customer.

```bash
curl https://[your-api-url]/prod/customers/1
```

### Step 7.4: Update Customer

**Why this step?** Verify that you can modify customer information.

```bash
curl -X PUT https://[your-api-url]/prod/customers/1 \
  -H "Content-Type: application/json" \
  -d '{
    "position": "IT Director",
    "status": "vip"
  }'
```

**Expected Response:**
```json
{
  "message": "Customer updated successfully",
  "id": 1
}
```

### Step 7.5: Record Interaction

**Why this step?** Verify that you can track customer interactions.

```bash
curl -X POST https://[your-api-url]/prod/customers/1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "description": "Sent commercial proposal"
  }'
```

**Expected Response:**
```json
{
  "message": "Interaction recorded successfully",
  "interaction_id": 1,
  "interaction_date": "2024-01-15T11:00:00"
}
```

### Step 7.6: Upload Document

**Why this step?** Verify that you can upload files associated with a customer.

```bash
# First, convert a file to base64
base64 document.pdf > document_base64.txt

# Then send the document
curl -X POST https://[your-api-url]/prod/customers/1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "contract.pdf",
    "file_type": "application/pdf",
    "file": "[base64 content here]"
  }'
```

**Expected Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": 1,
  "s3_key": "customers/1/uuid_contract.pdf",
  "uploaded_at": "2024-01-15T11:30:00"
}
```

### Step 7.7: Delete Customer

**Why this step?** Verify that you can remove customers from the system.

```bash
curl -X DELETE https://[your-api-url]/prod/customers/1
```

**Expected Response:**
```json
{
  "message": "Customer deleted successfully",
  "id": 1
}
```

---

## Part 8: Monitoring and Troubleshooting

### Introduction

Monitoring is essential for maintaining a healthy application. In this section, you'll learn how to view logs and metrics for your CRM system.

### CloudWatch Logs

**Why this step?** Logs help you debug issues and understand how your functions are performing.

1. Navigate to **CloudWatch** → **Log groups**
2. Search for `/aws/lambda/crm-*`
3. Click on any log group to view function logs
4. Each log stream represents a function invocation

   > 💡 **Tip**: Look for ERROR messages if something isn't working correctly.

### API Gateway Metrics

**Why this step?** Metrics help you understand usage patterns and identify performance issues.

1. Navigate to **API Gateway** → **CRM-API**
2. Click on **Dashboard**
3. View metrics for:
   - **Count**: Number of API calls
   - **Latency**: Response time
   - **4XX Errors**: Client errors (bad requests)
   - **5XX Errors**: Server errors

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Timeout errors | Lambda timeout too short | Increase timeout to 30+ seconds |
| Connection refused | Wrong RDS endpoint | Verify DB_HOST environment variable |
| Access denied | Missing IAM permissions | Check IAM role has correct policies |
| CORS errors | CORS not enabled | Enable CORS on API Gateway resources |

---

## Part 9: Cleanup

### Introduction

To avoid unexpected charges, it's important to delete all resources when you're finished with the lab. Follow these steps in order to ensure complete cleanup.

### Cleanup Steps

1. **API Gateway**
   - Navigate to **API Gateway**
   - Select `CRM-API`
   - Click **Actions** → **Delete API**

2. **Lambda Functions**
   - Navigate to **Lambda** → **Functions**
   - Delete all functions starting with `crm-`

3. **Lambda Layer**
   - Navigate to **Lambda** → **Layers**
   - Delete `psycopg2-layer`

4. **S3 Bucket**
   - Navigate to **S3**
   - Select your bucket `crm-documents-*`
   - Click **Empty** to delete all objects
   - Click **Delete** to remove the bucket

5. **RDS Instance**
   - Navigate to **RDS** → **Databases**
   - Select `crm-database`
   - Click **Actions** → **Delete**
   - Uncheck "Create final snapshot"
   - Confirm deletion

6. **IAM Resources**
   - Navigate to **IAM** → **Roles**
   - Delete `CRM-Lambda-Role`
   - Navigate to **IAM** → **Policies**
   - Delete `CRM-Lambda-Policy`

7. **Security Groups**
   - Navigate to **VPC** → **Security Groups**
   - Delete `crm-rds-sg` and `crm-lambda-sg`

   > ⚠️ **Note**: Wait for RDS deletion to complete before deleting security groups.

**Expected Result**: All resources deleted and no ongoing charges.

---

## End of Lab

Thank you for completing the AWS Lambda Hands-On Lab!

Remember: The best way to learn is by building. Start a project, experiment, and don't be afraid to make mistakes. The serverless community is here to help!

Kirk Patrick