# AWS Lambda Fundamentals - Hands-On Lab

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Lab 1: Environment Setup and First Lambda Function](#lab-1-environment-setup-and-first-lambda-function)
3. [Lab 2: API Gateway Integration](#lab-2-api-gateway-integration)
4. [Lab 3: Environment Variables and Configuration](#lab-3-environment-variables-and-configuration)
5. [Lab 4: Monitoring and CloudWatch Logs](#lab-4-monitoring-and-cloudwatch-logs)
6. [Lab 5: Lambda with S3 Triggers](#lab-5-lambda-with-s3-triggers)
7. [Lab 6: Infrastructure as Code with Terraform](#lab-6-infrastructure-as-code-with-terraform)
8. [Lab 7: Advanced Topics](#lab-7-advanced-topics)

---

## Prerequisites

### Theory: Understanding AWS Lambda

**AWS Lambda** is a serverless compute service that runs your code in response to events. Key concepts:
- **Event-driven execution**: Code runs only when triggered
- **Automatic scaling**: From zero to thousands of concurrent executions
- **Pay-per-use**: Charged only for compute time consumed
- **No server management**: AWS handles infrastructure, patching, and scaling

**Common Use Cases**:
- RESTful APIs (with API Gateway)
- Data processing (S3, DynamoDB streams)
- Scheduled tasks (EventBridge)
- Real-time file processing
- Backend for mobile/web applications

**Lambda Function Components**:
- **Handler**: Entry point function that AWS Lambda calls
- **Event**: Input data passed to your function
- **Context**: Runtime information about the execution
- **Runtime**: Execution environment (Python, Node.js, Java, etc.)

### Checklist
- [ ] Have an AWS account with administrative access
- [ ] Have AWS CLI installed or ready to install
- [ ] Basic understanding of Python or Node.js
- [ ] Text editor installed (VS Code recommended)
- [ ] Have a terminal/command line interface

---

## Lab 1: Environment Setup and First Lambda Function

### Theory: Lambda Function Fundamentals

A Lambda function consists of:
1. **Handler function**: The entry point (e.g., `lambda_handler` in Python)
2. **Event object**: Contains data from the invoking service
3. **Context object**: Provides runtime information
4. **Return value**: Response sent back to the caller

**Execution Model**:
- Lambda creates an execution environment (cold start)
- Environment is reused for subsequent invocations (warm start)
- Each function has its own isolated environment

### Tasks

#### 1.1 Verify AWS CLI Installation and Configuration

```bash
# Check AWS CLI version
aws --version

# Configure AWS credentials if not already done
aws configure

# Verify credentials
aws sts get-caller-identity
```

Expected output should show your AWS account ID and user information.

- [ ] AWS CLI installed and working
- [ ] Credentials configured correctly
- [ ] Account identity verified

**Reflection Question**: Why is it important to verify your AWS credentials before proceeding with Lambda development?

#### 1.2 Create Project Directory Structure

```bash
# Create lab directory
mkdir -p ~/lambda-lab
cd ~/lambda-lab

# Create subdirectories for different labs
mkdir -p lab1-basics lab2-api-gateway lab3-config lab4-monitoring lab5-s3-trigger lab6-terraform lab7-advanced

# Navigate to first lab
cd lab1-basics
```

- [ ] Directory structure created
- [ ] Navigated to lab1-basics directory

#### 1.3 Create Your First Lambda Function via Console

1. Log in to AWS Console at https://console.aws.amazon.com
2. Search for "Lambda" in the top search bar
3. Click **"Create function"**
4. Select **"Author from scratch"**
5. Configure:
   - **Function name**: `HelloWorldFunction`
   - **Runtime**: Python 3.12 (or latest available)
   - **Architecture**: x86_64
6. Click **"Create function"**

- [ ] Lambda function created successfully
- [ ] Function dashboard is visible

**Understanding Check**: What does "Author from scratch" mean versus using a blueprint?

#### 1.4 Write Your First Lambda Function

Replace the default code with:

```python
import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Basic Lambda function that returns a greeting message.
    
    Args:
        event: Input data from the trigger
        context: Runtime information
    
    Returns:
        Dictionary with statusCode and response body
    """
    
    # Get name from event or use default
    name = event.get('name', 'World')
    
    # Get current timestamp
    current_time = datetime.now().isoformat()
    
    # Build response message
    message = f"Hello, {name}! Lambda function executed at {current_time}"
    
    # Log to CloudWatch
    print(f"Function invoked with name: {name}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message,
            'input_event': event,
            'function_version': context.function_version,
            'request_id': context.request_id
        })
    }
```

- [ ] Code replaced in the console editor
- [ ] Code review completed

**Code Analysis Questions**:
1. What is the purpose of the `event` parameter?
2. What information does the `context` object provide?
3. Why do we return a dictionary with `statusCode` and `body`?

#### 1.5 Deploy and Test the Function

1. Click **"Deploy"** (orange button above the code editor)
2. Wait for "Successfully deployed" message
3. Click **"Test"** tab
4. Click **"Create new event"**
5. Configure test event:
   - **Event name**: `BasicTest`
   - **Event JSON**:
   ```json
   {
     "name": "DevOps Student"
   }
   ```
6. Click **"Save"**
7. Click **"Test"** button to execute

- [ ] Function deployed successfully
- [ ] Test event created
- [ ] Function executed without errors

**Expected Output**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Hello, DevOps Student! Lambda function executed at 2025-10-22T10:30:45.123456\", ...}"
}
```

**Execution Details** will show:
- Duration (in milliseconds)
- Billed Duration
- Memory Used
- Max Memory Used

- [ ] Response received successfully
- [ ] Execution metrics reviewed

**Reflection Questions**:
1. How much memory did your function use versus what was allocated?
2. What was the execution duration?
3. What would happen if you increased the allocated memory?

#### 1.6 Test with Different Inputs

Create additional test events:

**Test 2 - Empty Event**:
```json
{}
```

**Test 3 - Complex Event**:
```json
{
  "name": "Lambda Expert",
  "metadata": {
    "course": "DevOps Advanced",
    "lab": 1
  }
}
```

Run both tests and observe the outputs.

- [ ] Multiple test scenarios executed
- [ ] Default value behavior verified
- [ ] Different event structures tested

**Analysis Question**: How does the function handle the empty event? Why does this work?

#### 1.7 Save Function Code Locally

Create a local copy of your function:

```bash
cd ~/lambda-lab/lab1-basics
```

Create `lambda_function.py`:

```python
import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Basic Lambda function that returns a greeting message.
    """
    name = event.get('name', 'World')
    current_time = datetime.now().isoformat()
    message = f"Hello, {name}! Lambda function executed at {current_time}"
    
    print(f"Function invoked with name: {name}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message,
            'input_event': event,
            'function_version': context.function_version,
            'request_id': context.request_id
        })
    }
```

- [ ] Local copy of function created
- [ ] Code saved in lab1-basics directory

---

## Lab 2: API Gateway Integration

### Theory: Exposing Lambda via HTTP

**API Gateway** is a fully managed service that makes it easy to create, publish, and manage APIs at any scale. Integration with Lambda enables:
- RESTful API endpoints
- HTTP request/response handling
- Request validation and transformation
- Authentication and authorization
- Rate limiting and throttling

**Request Flow**:
1. Client sends HTTP request to API Gateway
2. API Gateway transforms request to Lambda event
3. Lambda processes event and returns response
4. API Gateway transforms response to HTTP format
5. Client receives HTTP response

**Event Structure**: API Gateway sends a different event structure than direct invocations, including:
- HTTP method
- Headers
- Query string parameters
- Path parameters
- Request body

### Tasks

#### 2.1 Add API Gateway Trigger

1. In your Lambda function console, click **"Add trigger"**
2. Select **"API Gateway"** from dropdown
3. Configure:
   - **Intent**: Create a new API
   - **API type**: REST API
   - **Security**: Open (for learning purposes)
4. Click **"Add"**

- [ ] API Gateway trigger added
- [ ] Trigger configuration visible in function overview

**Security Note**: In production, never use "Open" security. What authentication methods could you use instead?

#### 2.2 Locate Your API Endpoint

After creation, you'll see an **API endpoint** URL like:
```
https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction
```

- [ ] API endpoint URL copied
- [ ] URL structure understood

**URL Structure Analysis**: Break down the components of this URL. What does each part represent?

#### 2.3 Update Lambda Code for API Gateway

Replace your function code with:

```python
import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function designed for API Gateway integration.
    Handles HTTP requests and returns properly formatted responses.
    """
    
    # Log the complete event for debugging
    print(f"Received event: {json.dumps(event)}")
    
    # Extract HTTP method
    http_method = event.get('httpMethod', 'UNKNOWN')
    
    # Extract query parameters
    query_params = event.get('queryStringParameters') or {}
    name = query_params.get('name', 'World')
    
    # Extract path parameters
    path_params = event.get('pathParameters') or {}
    
    # Extract headers
    headers = event.get('headers') or {}
    user_agent = headers.get('User-Agent', 'Unknown')
    
    # Get request body if present
    body = event.get('body')
    if body:
        try:
            body_data = json.loads(body)
            name = body_data.get('name', name)
        except json.JSONDecodeError:
            pass
    
    # Build response
    current_time = datetime.now().isoformat()
    
    response_data = {
        'message': f'Hello, {name}!',
        'timestamp': current_time,
        'http_method': http_method,
        'user_agent': user_agent,
        'query_parameters': query_params
    }
    
    # Return API Gateway compatible response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # CORS support
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(response_data, indent=2)
    }
```

Click **"Deploy"**

- [ ] Code updated with API Gateway support
- [ ] Function deployed successfully

**Code Analysis**:
1. How is this code different from Lab 1?
2. Why do we need to handle `queryStringParameters` differently?
3. What is the purpose of the CORS headers?

#### 2.4 Test API Using Browser

Open your API endpoint URL in a browser:
```
https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction
```

Try with query parameters:
```
https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction?name=Student
```

- [ ] API accessible in browser
- [ ] Query parameters working correctly
- [ ] JSON response displayed

**Observation Question**: What happens when you refresh the page multiple times? Does the response change?

#### 2.5 Test API Using curl

```bash
# GET request with query parameter
curl "https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction?name=DevOps"

# POST request with JSON body
curl -X POST \
  "https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction" \
  -H "Content-Type: application/json" \
  -d '{"name": "API Tester", "course": "DevOps Advanced"}'

# GET request with headers
curl -H "Custom-Header: TestValue" \
  "https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction"
```

- [ ] GET request executed successfully
- [ ] POST request with body tested
- [ ] Custom headers sent and logged

**Analysis**: Compare the CloudWatch logs for each request type. What differences do you notice in the event structure?

#### 2.6 Create a Simple API Client Script

Create `api_client.py` in your lab2-api-gateway directory:

```python
import requests
import json

# Replace with your API endpoint
API_ENDPOINT = "https://your-api-id.execute-api.us-east-1.amazonaws.com/default/HelloWorldFunction"

def test_get_request():
    """Test GET request with query parameters."""
    print("\n=== Testing GET Request ===")
    params = {'name': 'Python Client'}
    response = requests.get(API_ENDPOINT, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_post_request():
    """Test POST request with JSON body."""
    print("\n=== Testing POST Request ===")
    payload = {
        'name': 'API Developer',
        'lab': 2,
        'topic': 'Lambda with API Gateway'
    }
    response = requests.post(API_ENDPOINT, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_get_request()
    test_post_request()
```

Run the script:
```bash
# Install requests if needed
pip install requests

# Run the client
python api_client.py
```

- [ ] API client script created
- [ ] Both GET and POST requests tested
- [ ] Responses validated

**Extension Challenge**: Modify the Lambda function to return different responses based on the HTTP method. How would you implement this?

---

## Lab 3: Environment Variables and Configuration

### Theory: Managing Configuration in Lambda

**Environment Variables** provide a way to:
- Store configuration separately from code
- Change behavior without redeploying code
- Manage secrets (though AWS Secrets Manager is preferred for sensitive data)
- Support different environments (dev, staging, production)

**Best Practices**:
- Never hardcode sensitive data in code
- Use descriptive variable names
- Document expected environment variables
- Use AWS Systems Manager Parameter Store or Secrets Manager for secrets

**Lambda Configuration Options**:
- Memory allocation (128 MB to 10,240 MB)
- Timeout (1 second to 15 minutes)
- Execution role (IAM permissions)
- VPC settings (for private resource access)

### Tasks

#### 3.1 Add Environment Variables

1. Go to your Lambda function
2. Click **"Configuration"** tab
3. Click **"Environment variables"** in left menu
4. Click **"Edit"**
5. Add the following variables:
   - Key: `GREETING_PREFIX` | Value: `Welcome`
   - Key: `GREETING_SUFFIX` | Value: `Thanks for using our API!`
   - Key: `ENVIRONMENT` | Value: `development`
   - Key: `MAX_RESPONSE_LENGTH` | Value: `500`
   - Key: `ENABLE_DEBUG_LOGGING` | Value: `true`
6. Click **"Save"**

- [ ] All environment variables added
- [ ] Variables saved successfully

**Conceptual Question**: Why is it better to use environment variables instead of hardcoding these values?

#### 3.2 Update Lambda Code to Use Environment Variables

```python
import json
import os
from datetime import datetime
import logging

# Configure logging based on environment variable
log_level = logging.DEBUG if os.environ.get('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true' else logging.INFO
logger = logging.getLogger()
logger.setLevel(log_level)

def lambda_handler(event, context):
    """
    Lambda function using environment variables for configuration.
    """
    
    # Read environment variables with defaults
    prefix = os.environ.get('GREETING_PREFIX', 'Hello')
    suffix = os.environ.get('GREETING_SUFFIX', 'Have a great day!')
    environment = os.environ.get('ENVIRONMENT', 'unknown')
    max_length = int(os.environ.get('MAX_RESPONSE_LENGTH', '1000'))
    
    # Log configuration (debug level)
    logger.debug(f"Configuration: prefix={prefix}, suffix={suffix}, env={environment}")
    
    # Extract request information
    http_method = event.get('httpMethod', 'UNKNOWN')
    query_params = event.get('queryStringParameters') or {}
    name = query_params.get('name', 'Developer')
    
    logger.info(f"Processing request for: {name}")
    
    # Build response message
    current_time = datetime.now().isoformat()
    message = f"{prefix}, {name}! {suffix}"
    
    # Truncate if exceeds max length
    if len(message) > max_length:
        message = message[:max_length] + "..."
        logger.warning(f"Message truncated to {max_length} characters")
    
    response_data = {
        'message': message,
        'timestamp': current_time,
        'environment': environment,
        'http_method': http_method,
        'function_config': {
            'memory_mb': context.memory_limit_in_mb,
            'remaining_time_ms': context.get_remaining_time_in_millis()
        }
    }
    
    logger.info("Request processed successfully")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-Environment': environment
        },
        'body': json.dumps(response_data, indent=2)
    }
```

Click **"Deploy"**

- [ ] Code updated with environment variable usage
- [ ] Logging configuration added
- [ ] Function deployed

**Code Review Questions**:
1. What happens if an environment variable doesn't exist?
2. Why do we use `os.environ.get()` instead of `os.environ['key']`?
3. How does the logging level affect what appears in CloudWatch?

#### 3.3 Test with Different Configurations

Test your API endpoint again and observe the new greeting format.

- [ ] API tested with new configuration
- [ ] Response shows environment variable values

#### 3.4 Modify Environment Variables

1. Go back to **Configuration** → **Environment variables**
2. Click **"Edit"**
3. Change:
   - `GREETING_PREFIX` to `Greetings`
   - `ENVIRONMENT` to `staging`
4. Click **"Save"**

Test the API again without redeploying code.

- [ ] Environment variables modified
- [ ] Changes reflected immediately in API response

**Key Insight**: Notice how you changed the behavior without modifying or redeploying code. When is this capability particularly valuable?

#### 3.5 Adjust Memory and Timeout Settings

1. Go to **Configuration** → **General configuration**
2. Click **"Edit"**
3. Modify settings:
   - **Memory**: Change to 256 MB
   - **Timeout**: Change to 10 seconds
4. Click **"Save"**

- [ ] Memory allocation increased
- [ ] Timeout increased

**Performance Question**: Test the function multiple times. Do you notice any difference in execution time with more memory?

#### 3.6 Create Configuration Documentation

Create `config.md` in your lab3-config directory:

```markdown
# Lambda Function Configuration

## Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| GREETING_PREFIX | Opening greeting text | "Hello" | "Welcome" |
| GREETING_SUFFIX | Closing message | "Have a great day!" | "Thanks!" |
| ENVIRONMENT | Current deployment environment | "unknown" | "production" |
| MAX_RESPONSE_LENGTH | Maximum characters in response | "1000" | "500" |
| ENABLE_DEBUG_LOGGING | Enable detailed logging | "false" | "true" |

## Resource Configuration

- **Memory**: 256 MB (affects CPU allocation)
- **Timeout**: 10 seconds
- **Runtime**: Python 3.12
- **Architecture**: x86_64

## Estimated Costs

Based on AWS pricing (as of 2025):
- Requests: $0.20 per 1M requests
- Duration: $0.0000166667 per GB-second
- Free tier: 1M requests + 400,000 GB-seconds per month

Example: 1M requests at 256 MB, 100ms avg = ~$0.50/month
```

- [ ] Configuration documentation created
- [ ] All variables documented

---

## Lab 4: Monitoring and CloudWatch Logs

### Theory: Observability in Serverless

**CloudWatch** provides monitoring and logging for AWS services. For Lambda:
- **Logs**: Captures all `print()` and `logger` output
- **Metrics**: Invocations, duration, errors, throttles
- **Alarms**: Automated notifications on metric thresholds
- **Insights**: Query and analyze logs at scale

**Log Structure**:
```
START RequestId: abc-123-def
[INFO] Your log message
END RequestId: abc-123-def
REPORT RequestId: abc-123-def Duration: 2.45 ms Billed: 3 ms Memory Size: 256 MB Max Memory Used: 45 MB
```

**Key Metrics**:
- **Invocations**: Total number of executions
- **Duration**: Time from start to finish
- **Errors**: Failed executions
- **Throttles**: Requests rejected due to concurrency limits
- **Concurrent Executions**: Simultaneous executions

### Tasks

#### 4.1 Access CloudWatch Logs

1. In your Lambda function, click **"Monitor"** tab
2. Click **"View CloudWatch logs"**
3. Click on the most recent **Log stream**

- [ ] CloudWatch Logs console accessed
- [ ] Recent log stream opened
- [ ] Log entries visible

**Log Analysis**: Find the START, log messages, END, and REPORT lines. What information does each provide?

#### 4.2 Enhance Function with Structured Logging

Update your Lambda function:

```python
import json
import os
from datetime import datetime
import logging

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(level, message, **kwargs):
    """Helper function for structured logging."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))

def lambda_handler(event, context):
    """
    Lambda function with comprehensive logging.
    """
    
    # Log function start
    log_event('INFO', 'Function execution started',
              request_id=context.request_id,
              function_version=context.function_version)
    
    try:
        # Extract configuration
        prefix = os.environ.get('GREETING_PREFIX', 'Hello')
        environment = os.environ.get('ENVIRONMENT', 'unknown')
        
        # Extract request data
        http_method = event.get('httpMethod', 'DIRECT_INVOKE')
        query_params = event.get('queryStringParameters') or {}
        name = query_params.get('name', 'Developer')
        
        # Log request details
        log_event('INFO', 'Processing request',
                  http_method=http_method,
                  name=name,
                  environment=environment)
        
        # Build response
        current_time = datetime.now().isoformat()
        message = f"{prefix}, {name}!"
        
        response_data = {
            'message': message,
            'timestamp': current_time,
            'environment': environment,
            'request_id': context.request_id
        }
        
        # Log successful processing
        log_event('INFO', 'Request processed successfully',
                  response_length=len(json.dumps(response_data)),
                  execution_time_remaining=context.get_remaining_time_in_millis())
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': context.request_id
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        # Log errors with full context
        log_event('ERROR', 'Function execution failed',
                  error_type=type(e).__name__,
                  error_message=str(e),
                  request_id=context.request_id)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'request_id': context.request_id
            })
        }
```

Deploy and test the function.

- [ ] Enhanced logging implemented
- [ ] Function tested via API
- [ ] Structured logs visible in CloudWatch

**Log Structure Question**: Why is structured (JSON) logging better than plain text for production systems?

#### 4.3 Generate Different Log Scenarios

Create test events to generate various log patterns:

**Success Test**:
```bash
curl "https://your-api-endpoint/default/HelloWorldFunction?name=TestUser"
```

**Error Test** - Create a new Lambda function test event:
```json
{
  "httpMethod": "POST",
  "queryStringParameters": null,
  "body": "invalid json content{{"
}
```

Modify your code to attempt parsing the body and catch the error.

- [ ] Multiple scenarios tested
- [ ] Different log levels generated
- [ ] Error handling verified

#### 4.4 Analyze CloudWatch Metrics

1. Go to **Monitor** tab in Lambda console
2. Review the following metrics:
   - **Invocations** (last hour)
   - **Duration** (average and percentiles)
   - **Error count and success rate**
   - **Throttles**

- [ ] All metrics reviewed
- [ ] Metric trends understood

**Metric Analysis**:
1. What was your average execution duration?
2. What was the p99 (99th percentile) duration?
3. Why might p99 be significantly higher than average?

#### 4.5 Create CloudWatch Insights Query

1. In CloudWatch Logs console, click **"Logs Insights"**
2. Select your Lambda function's log group
3. Enter this query:

```
fields @timestamp, @message
| filter @message like /Processing request/
| stats count() by bin(5m)
```

4. Click **"Run query"**

Try this query to find errors:
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

- [ ] CloudWatch Insights accessed
- [ ] Queries executed successfully
- [ ] Results analyzed

**Query Challenge**: Write a query to calculate the average execution time for requests by name parameter.

#### 4.6 Set Up a CloudWatch Alarm

1. Go to CloudWatch console
2. Click **"Alarms"** → **"Create alarm"**
3. Click **"Select metric"**
4. Navigate to **Lambda** → **By Function Name**
5. Select your function and **Errors** metric
6. Configure:
   - **Statistic**: Sum
   - **Period**: 5 minutes
   - **Threshold**: Greater than 5
7. Configure notification (optional - requires SNS topic)
8. Name alarm: `HelloWorldFunction-Errors`
9. Click **"Create alarm"**

- [ ] CloudWatch Alarm created
- [ ] Threshold configured appropriately

**Design Question**: Why did we choose 5 errors in 5 minutes as the threshold? How would you determine appropriate thresholds for production?

---

## Lab 5: Lambda with S3 Triggers

### Theory: Event-Driven Architecture with S3

**S3 Events** trigger Lambda functions when:
- Objects are created (PUT, POST, COPY)
- Objects are deleted
- Objects are restored from Glacier
- Replication events occur

**Common Use Cases**:
- Image thumbnail generation
- Log file processing
- Data transformation pipelines
- Content validation
- Automated backups

**Event Structure**: S3 sends detailed event information including:
- Bucket name
- Object key (file path)
- Event type
- Object size
- Timestamp

### Tasks

#### 5.1 Create an S3 Bucket

```bash
# Generate unique bucket name
BUCKET_NAME="lambda-lab-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME

# Verify bucket creation
aws s3 ls | grep lambda-lab

echo "Bucket created: $BUCKET_NAME"
echo "Save this bucket name for later steps"
```

- [ ] S3 bucket created successfully
- [ ] Bucket name saved

**Planning Question**: Before creating the Lambda function, think about what you want it to do when a file is uploaded. What are some practical use cases?

#### 5.2 Create Lambda Function for S3 Processing

1. Create a new Lambda function:
   - Name: `S3FileProcessor`
   - Runtime: Python 3.12
2. Replace code with:

```python
import json
import urllib.parse
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Process S3 events - triggered when files are uploaded.
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Process each record in the event
    for record in event['Records']:
        # Extract S3 event information
        event_name = record['eventName']
        bucket_name = record['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        object_size = record['s3']['object']['size']
        
        print(f"Event: {event_name}")
        print(f"Bucket: {bucket_name}")
        print(f"File: {object_key}")
        print(f"Size: {object_size} bytes")
        
        # Get object metadata
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            content_type = response.get('ContentType', 'unknown')
            
            print(f"Content Type: {content_type}")
            
            # Process based on file type
            if content_type.startswith('text/'):
                process_text_file(bucket_name, object_key)
            elif content_type.startswith('image/'):
                process_image_file(bucket_name, object_key)
            else:
                print(f"Unhandled content type: {content_type}")
            
        except Exception as e:
            print(f"Error processing {object_key}: {str(e)}")
            raise
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }

def process_text_file(bucket, key):
    """Process text files - count lines and words."""
    print(f"Processing text file: {key}")
    
    try:
        # Download file content
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        # Analyze content
        lines = content.split('\n')
        words = content.split()
        
        print(f"Lines: {len(lines)}")
        print(f"Words: {len(words)}")
        print(f"Characters: {len(content)}")
        
        # Create analysis result
        analysis = {
            'file': key,
            'lines': len(lines),
            'words': len(words),
            'characters': len(content)
        }
        
        # Save analysis to new file
        analysis_key = f"analysis/{key}.json"
        s3_client.put_object(
            Bucket=bucket,
            Key=analysis_key,
            Body=json.dumps(analysis, indent=2),
            ContentType='application/json'
        )
        
        print(f"Analysis saved to: {analysis_key}")
        
    except Exception as e:
        print(f"Error processing text file: {str(e)}")
        raise

def process_image_file(bucket, key):
    """Process image files - log metadata."""
    print(f"Processing image file: {key}")
    print("Image processing would happen here (e.g., resize, thumbnail)")
```

3. Click **"Deploy"**

- [ ] S3FileProcessor function created
- [ ] Code deployed

**Code Understanding**:
1. How does the function access S3 object information?
2. What is `urllib.parse.unquote_plus` used for?
3. Why do we need to handle different content types?

#### 5.3 Add S3 Permissions to Lambda Role

1. Go to **Configuration** → **Permissions**
2. Click on the **Role name** (opens IAM console)
3. Click **"Add permissions"** → **"Attach policies"**
4. Search for and select: `AmazonS3FullAccess` (for learning - use minimal permissions in production)
5. Click **"Attach policies"**

- [ ] S3 permissions added to Lambda role
- [ ] Policy attachment verified

**Security Question**: Why is `AmazonS3FullAccess` not recommended for production? What specific permissions would you grant instead?

#### 5.4 Configure S3 Trigger

1. In S3FileProcessor function, click **"Add trigger"**
2. Select **"S3"**
3. Configure:
   - **Bucket**: Select your lambda-lab bucket
   - **Event types**: All object create events
   - **Prefix**: (leave empty to process all files)
   - **Suffix**: (leave empty)
4. Acknowledge the checkbox
5. Click **"Add"**

- [ ] S3 trigger configured
- [ ] Trigger appears in function overview

#### 5.5 Test S3 Trigger

Create test files and upload:

```bash
# Set your bucket name
BUCKET_NAME="your-lambda-lab-bucket-name"

# Create test text file
echo "This is a test file for Lambda processing.
It has multiple lines.
Each line will be counted.
Lambda is awesome!" > test-file.txt

# Upload file
aws s3 cp test-file.txt s3://$BUCKET_NAME/

# Check if analysis file was created
sleep 5
aws s3 ls s3://$BUCKET_NAME/analysis/

# Download and view analysis
aws s3 cp s3://$BUCKET_NAME/analysis/test-file.txt.json analysis-result.json
cat analysis-result.json
```

- [ ] Test file uploaded
- [ ] Lambda function triggered automatically
- [ ] Analysis file created in S3

**Observation**: Check CloudWatch Logs. You should see the processing logs appear automatically when you upload files.

#### 5.6 Test with Multiple Files

```bash
# Upload multiple files
for i in {1..5}; do
  echo "Test file number $i with some content" > test-$i.txt
  aws s3 cp test-$i.txt s3://$BUCKET_NAME/
done

# Wait and check results
sleep 5
aws s3 ls s3://$BUCKET_NAME/analysis/
```

- [ ] Multiple files uploaded
- [ ] All files processed
- [ ] Analysis files generated for each

**Performance Question**: Upload 10 files simultaneously. How many Lambda instances are created? Check CloudWatch metrics for concurrent executions.

#### 5.7 Create Monitoring Script

Create `monitor_s3_processing.py`:

```python
import boto3
import time
from datetime import datetime

s3_client = boto3.client('s3')
logs_client = boto3.client('logs')

BUCKET_NAME = "your-lambda-lab-bucket-name"
LOG_GROUP = "/aws/lambda/S3FileProcessor"

def count_files():
    """Count files in bucket and analysis folder."""
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    total_files = response.get('KeyCount', 0)
    
    analysis_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='analysis/'
    )
    analysis_files = analysis_response.get('KeyCount', 0)
    
    return total_files, analysis_files

def get_recent_logs():
    """Get recent Lambda execution logs."""
    try:
        streams = logs_client.describe_log_streams(
            logGroupName=LOG_GROUP,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if streams['logStreams']:
            stream_name = streams['logStreams'][0]['logStreamName']
            events = logs_client.get_log_events(
                logGroupName=LOG_GROUP,
                logStreamName=stream_name,
                limit=10
            )
            return events['events']
    except Exception as e:
        print(f"Error getting logs: {e}")
    
    return []

if __name__ == "__main__":
    print("S3 Lambda Processing Monitor")
    print("=" * 50)
    
    total, analyzed = count_files()
    print(f"Total files in bucket: {total}")
    print(f"Analysis files created: {analyzed}")
    
    print("\nRecent Lambda logs:")
    for event in get_recent_logs():
        timestamp = datetime.fromtimestamp(event['timestamp']/1000)
        print(f"[{timestamp}] {event['message']}")
```

- [ ] Monitoring script created
- [ ] Script executed successfully

---

## Lab 6: Infrastructure as Code with Terraform

### Theory: Managing Lambda with Terraform

**Infrastructure as Code (IaC)** benefits:
- Version control for infrastructure
- Reproducible deployments
- Automated provisioning
- Documentation through code
- Team collaboration

**Terraform Lambda Resources**:
- `aws_lambda_function`: The function itself
- `aws_iam_role`: Execution role
- `aws_lambda_permission`: Invoke permissions
- `aws_cloudwatch_log_group`: Log management

**Workflow**:
1. Write Terraform configuration
2. Initialize Terraform (`terraform init`)
3. Plan changes (`terraform plan`)
4. Apply changes (`terraform apply`)
5. Manage state

### Tasks

#### 6.1 Install Terraform

```bash
# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# macOS
brew install terraform

# Verify
terraform version
```

- [ ] Terraform installed
- [ ] Version verified

#### 6.2 Create Terraform Project Structure

```bash
cd ~/lambda-lab/lab6-terraform

# Create directory structure
mkdir -p lambda-code
mkdir -p terraform
```

- [ ] Project structure created

#### 6.3 Create Lambda Function Code

Create `lambda-code/lambda_function.py`:

```python
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function deployed via Terraform.
    """
    
    environment = os.environ.get('ENVIRONMENT', 'unknown')
    app_version = os.environ.get('APP_VERSION', '1.0.0')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': 'Hello from Terraform-managed Lambda!',
            'environment': environment,
            'version': app_version,
            'timestamp': datetime.now().isoformat()
        })
    }
```

Create `lambda-code/requirements.txt`:
```
# No external dependencies for this example
```

- [ ] Lambda code created
- [ ] Requirements file created

#### 6.4 Create Terraform Configuration

Create `terraform/main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Create ZIP file of Lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda-code"
  output_path = "${path.module}/lambda_function.zip"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# Lambda Function
resource "aws_lambda_function" "main" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = var.runtime
  timeout         = var.timeout
  memory_size     = var.memory_size

  environment {
    variables = var.environment_variables
  }

  tags = var.tags

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_basic
  ]
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.function_name}-api"
  description = "API Gateway for ${var.function_name}"

  tags = var.tags
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.main.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  depends_on = [
    aws_api_gateway_integration.lambda
  ]

  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = var.api_stage_name
}
```

Create `terraform/variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "function_name" {
  description = "Lambda function name"
  type        = string
  default     = "terraform-managed-lambda"
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.12"
}

variable "timeout" {
  description = "Function timeout in seconds"
  type        = number
  default     = 10
}

variable "memory_size" {
  description = "Memory allocation in MB"
  type        = number
  default     = 256
}

variable "log_retention_days" {
  description = "CloudWatch log retention"
  type        = number
  default     = 7
}

variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "prod"
}

variable "environment_variables" {
  description = "Environment variables for Lambda"
  type        = map(string)
  default = {
    ENVIRONMENT = "production"
    APP_VERSION = "1.0.0"
  }
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Project     = "Lambda Lab"
    ManagedBy   = "Terraform"
    Environment = "Learning"
  }
}
```

Create `terraform/outputs.tf`:

```hcl
output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.main.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.main.function_name
}

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_deployment.main.invoke_url}"
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}
```

- [ ] All Terraform files created
- [ ] Configuration reviewed

**Configuration Review**:
1. How does Terraform package the Lambda code?
2. What IAM permissions are granted to the function?
3. How is the API Gateway connected to Lambda?

#### 6.5 Initialize and Apply Terraform

```bash
cd ~/lambda-lab/lab6-terraform/terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Preview changes
terraform plan

# Apply configuration
terraform apply
```

Type `yes` when prompted.

- [ ] Terraform initialized
- [ ] Configuration validated
- [ ] Plan reviewed
- [ ] Resources created

**Deployment Question**: Review the `terraform plan` output. How many resources will be created? Can you identify each one?

#### 6.6 Test the Deployed Function

```bash
# Get API endpoint from output
API_URL=$(terraform output -raw api_gateway_url)

# Test the endpoint
curl $API_URL

# Test with API Gateway deployed path
curl "$API_URL/prod"
```

- [ ] API endpoint retrieved
- [ ] Function tested successfully
- [ ] Response validated

#### 6.7 Update Lambda Configuration via Terraform

Edit `terraform/variables.tf` to modify `environment_variables`:

```hcl
variable "environment_variables" {
  description = "Environment variables for Lambda"
  type        = map(string)
  default = {
    ENVIRONMENT = "production"
    APP_VERSION = "2.0.0"
    FEATURE_FLAG = "enabled"
  }
}
```

Apply changes:

```bash
terraform plan
terraform apply
```

- [ ] Configuration updated
- [ ] Changes applied
- [ ] Function behavior updated

**IaC Benefits**: Notice how you updated the infrastructure by just changing code. What advantages does this provide?

#### 6.8 View Terraform State

```bash
# List resources in state
terraform state list

# Show specific resource details
terraform state show aws_lambda_function.main

# View outputs
terraform output
```

- [ ] State file examined
- [ ] Resource details reviewed
- [ ] Outputs displayed

#### 6.9 Destroy Infrastructure

```bash
# Preview destruction
terraform plan -destroy

# Destroy all resources
terraform destroy
```

Type `yes` when prompted.

- [ ] Destruction plan reviewed
- [ ] All resources destroyed
- [ ] AWS console verified clean

**Cleanup Question**: Why is it important to destroy resources you're not using? How does Terraform make this process safer?

---

## Lab 7: Advanced Topics

### Theory: Advanced Lambda Patterns

**Lambda Layers**:
- Share code and dependencies across functions
- Reduce deployment package size
- Centralize common utilities
- Version dependencies independently

**Asynchronous Invocation**:
- Lambda returns immediately with 202 status
- Function executes in background
- Automatic retries on failure
- Dead Letter Queue (DLQ) for failed events

**Concurrency Control**:
- Reserved concurrency: Guarantees capacity
- Provisioned concurrency: Pre-warmed instances
- Throttling: Protects downstream systems

### Tasks

#### 7.1 Create a Lambda Layer

Create `lab7-advanced/layer-content/python/common_utils.py`:

```python
import json
from datetime import datetime
from typing import Dict, Any

def format_response(status_code: int, data: Any, message: str = "") -> Dict:
    """
    Standard API response formatter.
    """
    response = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    if message:
        response['message'] = message
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'X-Custom-Header': 'Lambda-Lab'
        },
        'body': json.dumps(response)
    }

def validate_input(event: Dict, required_fields: list) -> tuple:
    """
    Validate required fields in input.
    Returns (is_valid, missing_fields)
    """
    query_params = event.get('queryStringParameters') or {}
    missing = [field for field in required_fields if field not in query_params]
    
    return (len(missing) == 0, missing)

class DataProcessor:
    """
    Common data processing utilities.
    """
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Remove special characters and trim."""
        return ''.join(char for char in text if char.isalnum() or char.isspace()).strip()
    
    @staticmethod
    def calculate_metrics(data: list) -> Dict:
        """Calculate basic metrics for a list of numbers."""
        if not data:
            return {}
        
        return {
            'count': len(data),
            'sum': sum(data),
            'average': sum(data) / len(data),
            'min': min(data),
            'max': max(data)
        }
```

Package the layer:

```bash
cd ~/lambda-lab/lab7-advanced

# Create layer ZIP
cd layer-content
zip -r ../common-layer.zip python/
cd ..
```

- [ ] Layer code created
- [ ] Layer packaged as ZIP

#### 7.2 Deploy Layer via AWS CLI

```bash
# Upload layer
aws lambda publish-layer-version \
    --layer-name common-utilities \
    --description "Common utilities for Lambda functions" \
    --zip-file fileb://common-layer.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures x86_64

# Note the LayerVersionArn from output
```

- [ ] Layer published
- [ ] Layer ARN saved

**Layer Concept**: How is a layer different from including code directly in your function?

#### 7.3 Create Function Using Layer

Create a new Lambda function named `AdvancedProcessor`:

```python
import json
# Import from layer
from common_utils import format_response, validate_input, DataProcessor

def lambda_handler(event, context):
    """
    Lambda function using shared layer utilities.
    """
    
    print(f"Processing event with layer utilities")
    
    # Validate input
    required_fields = ['operation']
    is_valid, missing = validate_input(event, required_fields)
    
    if not is_valid:
        return format_response(
            400,
            {'error': f'Missing required fields: {missing}'},
            'Validation failed'
        )
    
    query_params = event.get('queryStringParameters', {})
    operation = query_params.get('operation')
    
    if operation == 'metrics':
        # Sample data for metrics calculation
        data = [10, 20, 30, 40, 50]
        metrics = DataProcessor.calculate_metrics(data)
        
        return format_response(
            200,
            {'metrics': metrics, 'operation': operation},
            'Metrics calculated successfully'
        )
    
    elif operation == 'sanitize':
        text = query_params.get('text', '')
        sanitized = DataProcessor.sanitize_string(text)
        
        return format_response(
            200,
            {'original': text, 'sanitized': sanitized},
            'Text sanitized successfully'
        )
    
    else:
        return format_response(
            400,
            {'error': f'Unknown operation: {operation}'},
            'Invalid operation'
        )
```

Add the layer to your function:
1. Go to function configuration
2. Click **"Layers"**
3. Click **"Add a layer"**
4. Select **"Custom layers"**
5. Choose your `common-utilities` layer
6. Click **"Add"**

- [ ] Function created with layer
- [ ] Layer attached successfully
- [ ] Function tested

**Test the function**:
```bash
curl "https://your-api-endpoint?operation=metrics"
curl "https://your-api-endpoint?operation=sanitize&text=Hello%20World%21%40%23"
```

#### 7.4 Configure Asynchronous Invocation

Create a new function `AsyncProcessor`:

```python
import json
import time
import random

def lambda_handler(event, context):
    """
    Simulate long-running asynchronous processing.
    """
    
    task_id = event.get('task_id', 'unknown')
    processing_time = random.randint(2, 5)
    
    print(f"Starting task {task_id}")
    print(f"Estimated processing time: {processing_time} seconds")
    
    # Simulate processing
    time.sleep(processing_time)
    
    # Randomly simulate failure for testing
    if random.random() < 0.2:  # 20% failure rate
        print(f"Task {task_id} failed")
        raise Exception(f"Processing failed for task {task_id}")
    
    print(f"Task {task_id} completed successfully")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'task_id': task_id,
            'processing_time': processing_time,
            'status': 'completed'
        })
    }
```

Configure async settings:
1. Go to **Configuration** → **Asynchronous invocation**
2. Click **"Edit"**
3. Set:
   - **Maximum age of event**: 3600 seconds
   - **Retry attempts**: 2
4. Click **"Save"**

- [ ] Async function created
- [ ] Retry policy configured

#### 7.5 Create SQS Dead Letter Queue

```bash
# Create DLQ
aws sqs create-queue --queue-name lambda-dlq

# Get queue ARN
QUEUE_ARN=$(aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/YOUR-ACCOUNT-ID/lambda-dlq \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "DLQ ARN: $QUEUE_ARN"
```

Add DLQ to Lambda function:
1. Edit async invocation settings
2. Under **"Destination"** → **"On failure"**
3. Select **"SQS queue"**
4. Enter your queue ARN
5. Click **"Save"**

- [ ] DLQ created
- [ ] DLQ configured for Lambda

**Design Question**: Why use a Dead Letter Queue? What would you do with failed events?

#### 7.6 Invoke Function Asynchronously

```bash
# Invoke asynchronously
aws lambda invoke \
    --function-name AsyncProcessor \
    --invocation-type Event \
    --payload '{"task_id": "task-001"}' \
    response.json

# Check response (should return 202 Accepted)
cat response.json
```

Invoke multiple times:
```bash
for i in {1..10}; do
    aws lambda invoke \
        --function-name AsyncProcessor \
        --invocation-type Event \
        --payload "{\"task_id\": \"task-$i\"}" \
        response-$i.json
    echo "Invoked task-$i"
done
```

- [ ] Async invocations successful
- [ ] 202 status codes received
- [ ] CloudWatch logs show processing

**Monitoring**: Check CloudWatch Logs. Notice how invocations don't block. Some may fail and retry.

#### 7.7 Configure Reserved Concurrency

1. Go to **Configuration** → **Concurrency**
2. Click **"Edit"**
3. Select **"Reserve concurrency"**
4. Set value: **5**
5. Click **"Save"**

Test with burst traffic:

```bash
# Generate concurrent requests
for i in {1..20}; do
    aws lambda invoke \
        --function-name AsyncProcessor \
        --invocation-type Event \
        --payload "{\"task_id\": \"burst-$i\"}" \
        burst-$i.json &
done

wait
```

- [ ] Reserved concurrency configured
- [ ] Burst test executed
- [ ] Throttling observed (if 20 > 5)

**Concurrency Question**: Check CloudWatch metrics for throttles. Why would you limit concurrency on purpose?

#### 7.8 Create Integration Test Suite

Create `test_lambda_functions.py`:

```python
import boto3
import json
import time
from datetime import datetime

lambda_client = boto3.client('lambda')
logs_client = boto3.client('logs')

def test_sync_invocation(function_name):
    """Test synchronous Lambda invocation."""
    print(f"\n{'='*60}")
    print(f"Testing Synchronous Invocation: {function_name}")
    print(f"{'='*60}")
    
    payload = {'name': 'Test User', 'test_id': str(time.time())}
    
    start_time = time.time()
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    duration = time.time() - start_time
    
    result = json.loads(response['Payload'].read())
    
    print(f"✓ Status Code: {response['StatusCode']}")
    print(f"✓ Duration: {duration:.2f}s")
    print(f"✓ Response: {json.dumps(result, indent=2)}")
    
    return response['StatusCode'] == 200

def test_async_invocation(function_name, num_invocations=5):
    """Test asynchronous Lambda invocations."""
    print(f"\n{'='*60}")
    print(f"Testing Async Invocation: {function_name}")
    print(f"{'='*60}")
    
    for i in range(num_invocations):
        payload = {'task_id': f'test-{i}', 'timestamp': datetime.now().isoformat()}
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        
        print(f"✓ Task {i}: Status {response['StatusCode']}")
    
    print(f"\n✓ Sent {num_invocations} async invocations")
    print("Check CloudWatch Logs for processing results")

def get_function_metrics(function_name, minutes=5):
    """Get CloudWatch metrics for function."""
    print(f"\n{'='*60}")
    print(f"Function Metrics: {function_name}")
    print(f"{'='*60}")
    
    cloudwatch = boto3.client('cloudwatch')
    
    end_time = datetime.now()
    start_time = datetime.fromtimestamp(end_time.timestamp() - minutes*60)
    
    metrics = ['Invocations', 'Errors', 'Throttles', 'Duration']
    
    for metric_name in metrics:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName=metric_name,
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Sum', 'Average']
        )
        
        if response['Datapoints']:
            datapoint = response['Datapoints'][0]
            print(f"✓ {metric_name}: {datapoint}")
        else:
            print(f"○ {metric_name}: No data")

if __name__ == "__main__":
    print("\nLambda Integration Test Suite")
    print("="*60)
    
    # Test your functions
    SYNC_FUNCTION = "HelloWorldFunction"
    ASYNC_FUNCTION = "AsyncProcessor"
    
    # Run tests
    test_sync_invocation(SYNC_FUNCTION)
    test_async_invocation(ASYNC_FUNCTION, 3)
    
    # Wait for async processing
    print("\nWaiting for async processing...")
    time.sleep(10)
    
    # Get metrics
    get_function_metrics(SYNC_FUNCTION)
    get_function_metrics(ASYNC_FUNCTION)
    
    print("\n✓ All tests completed!")
```

Run tests:
```bash
pip install boto3
python test_lambda_functions.py
```

- [ ] Test suite created
- [ ] All tests executed
- [ ] Metrics collected

---

When building production Lambda functions, remember:

- [ ] **Security**
  - Use least-privilege IAM roles
  - Store secrets in AWS Secrets Manager
  - Enable encryption at rest and in transit
  - Implement authentication on API Gateway

- [ ] **Performance**
  - Right-size memory allocation
  - Minimize cold starts (use provisioned concurrency if needed)
  - Optimize package size
  - Reuse connections and SDK clients

- [ ] **Reliability**
  - Implement proper error handling
  - Configure retries and DLQs
  - Set appropriate timeouts
  - Monitor and alert on errors

- [ ] **Observability**
  - Use structured logging
  - Add custom metrics
  - Implement distributed tracing (X-Ray)
  - Set up CloudWatch dashboards

- [ ] **Cost Optimization**
  - Monitor and optimize memory usage
  - Use async invocation when possible
  - Clean up unused functions
  - Leverage free tier effectively

### Additional Resources

#### Official Documentation
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)

#### Tools and Frameworks
- **AWS SAM**: Simplified deployment for serverless apps
- **Serverless Framework**: Multi-cloud serverless framework
- **AWS CDK**: Infrastructure as code using programming languages
- **LocalStack**: Local AWS cloud emulation

### Cost Management Tips

**Understanding Lambda Pricing (2025)**:
- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Free Tier**: 1M requests + 400,000 GB-seconds per month (permanent)

**Example Calculations**:

| Scenario | Requests/Month | Memory | Avg Duration | Monthly Cost |
|----------|----------------|--------|--------------|--------------|
| Small API | 100,000 | 128 MB | 100ms | ~$0.05 |
| Medium API | 1,000,000 | 256 MB | 200ms | ~$0.60 |
| Large API | 5,000,000 | 512 MB | 300ms | ~$5.00 |
| Batch Job | 10,000 | 1024 MB | 30s | ~$5.00 |

**Cost Optimization Strategies**:
1. Use appropriate memory allocation (test different sizes)
2. Optimize cold starts
3. Use provisioned concurrency only when needed
4. Clean up old function versions
5. Monitor and set billing alarms

### Troubleshooting Guide

#### Common Issues and Solutions

**Problem: Function timing out**
- **Solution**: 
  - Increase timeout in configuration
  - Optimize code for better performance
  - Check for hanging connections or slow API calls
  - Use async patterns for long-running tasks

**Problem: Out of memory errors**
- **Solution**:
  - Increase memory allocation
  - Optimize data structures
  - Stream large files instead of loading in memory
  - Clear unused variables

**Problem: Cold start latency**
- **Solution**:
  - Minimize deployment package size
  - Use Lambda Layers for dependencies
  - Consider provisioned concurrency
  - Implement lazy loading for heavy imports

**Problem: Permission denied errors**
- **Solution**:
  - Review IAM role policies
  - Check resource-based policies
  - Verify execution role trust relationship
  - Use AWS Policy Simulator for testing

**Problem: API Gateway 502/504 errors**
- **Solution**:
  - Verify Lambda response format
  - Check function timeout vs API Gateway timeout
  - Review CloudWatch logs for exceptions
  - Ensure proper CORS headers

**Problem: Can't find logs in CloudWatch**
- **Solution**:
  - Verify CloudWatch Logs permissions in execution role
  - Check log group retention settings
  - Ensure function is being invoked
  - Use correct log group name format: `/aws/lambda/function-name`

### Lab Cleanup

To avoid unnecessary charges, clean up resources:

#### Manual Cleanup
1. **Lambda Functions**:
   ```bash
   aws lambda delete-function --function-name HelloWorldFunction
   aws lambda delete-function --function-name S3FileProcessor
   aws lambda delete-function --function-name AsyncProcessor
   aws lambda delete-function --function-name AdvancedProcessor
   ```

2. **API Gateways**:
   - Go to API Gateway console
   - Select each API
   - Click "Actions" → "Delete"

3. **S3 Buckets**:
   ```bash
   # Empty bucket first
   aws s3 rm s3://your-bucket-name --recursive
   # Delete bucket
   aws s3 rb s3://your-bucket-name
   ```

4. **CloudWatch Log Groups**:
   ```bash
   aws logs delete-log-group --log-group-name /aws/lambda/HelloWorldFunction
   # Repeat for other functions
   ```

5. **Lambda Layers**:
   ```bash
   aws lambda delete-layer-version \
     --layer-name common-utilities \
     --version-number 1
   ```

6. **SQS Queues**:
   ```bash
   aws sqs delete-queue --queue-url https://sqs.us-east-1.amazonaws.com/ACCOUNT/lambda-dlq
   ```

7. **IAM Roles**:
   - Go to IAM console
   - Delete Lambda execution roles created during labs

#### Terraform Cleanup
If you deployed via Terraform:
```bash
cd ~/lambda-lab/lab6-terraform/terraform
terraform destroy
```

## Appendix A: Quick Reference Commands

### AWS CLI Lambda Commands

```bash
# List functions
aws lambda list-functions

# Get function configuration
aws lambda get-function-configuration --function-name MyFunction

# Invoke function
aws lambda invoke --function-name MyFunction response.json

# Update function code
aws lambda update-function-code \
  --function-name MyFunction \
  --zip-file fileb://function.zip

# Update function configuration
aws lambda update-function-configuration \
  --function-name MyFunction \
  --timeout 30 \
  --memory-size 512

# Get function logs
aws logs tail /aws/lambda/MyFunction --follow

# Create function
aws lambda create-function \
  --function-name MyFunction \
  --runtime python3.12 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

### Common Lambda Code Patterns

#### Basic Handler
```python
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello World')
    }
```

#### API Gateway Handler
```python
def lambda_handler(event, context):
    body = json.loads(event['body'])
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Success'})
    }
```

#### S3 Event Handler
```python
def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        # Process file
```

#### Error Handling
```python
def lambda_handler(event, context):
    try:
        # Your code
        return {'statusCode': 200}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'statusCode': 500}
```

---

## Appendix B: Python Requirements Template

```txt
# requirements.txt for Lambda

# AWS SDK (included by default, but you can pin version)
boto3==1.34.0
botocore==1.34.0

# Common utilities
requests==2.31.0
python-dateutil==2.8.2

# Data processing
pandas==2.1.4
numpy==1.26.2

# JSON/YAML handling
pyyaml==6.0.1

# Environment variables
python-dotenv==1.0.0

# HTTP clients
httpx==0.25.2

# Validation
pydantic==2.5.2

# Database
pymongo==4.6.0
psycopg2-binary==2.9.9

# Testing
pytest==7.4.3
moto==4.2.9  # AWS mocking
```

---

## Appendix C: Terraform Modules Example

### Reusable Lambda Module

Create `modules/lambda/main.tf`:

```hcl
variable "function_name" {
  type = string
}

variable "runtime" {
  type    = string
  default = "python3.12"
}

variable "handler" {
  type    = string
  default = "lambda_function.lambda_handler"
}

variable "source_dir" {
  type = string
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/lambda_${var.function_name}.zip"
}

resource "aws_lambda_function" "this" {
  filename         = data.archive_file.lambda.output_path
  function_name    = var.function_name
  role            = aws_iam_role.lambda.arn
  handler         = var.handler
  runtime         = var.runtime
  source_code_hash = data.archive_file.lambda.output_base64sha256

  environment {
    variables = var.environment_variables
  }
}

resource "aws_iam_role" "lambda" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "function_arn" {
  value = aws_lambda_function.this.arn
}

output "function_name" {
  value = aws_lambda_function.this.function_name
}
```

### Using the Module

```hcl
module "my_lambda" {
  source = "./modules/lambda"

  function_name = "my-awesome-function"
  source_dir    = "${path.module}/../lambda-code"
  
  environment_variables = {
    ENV = "production"
  }
}
```

---

## Appendix D: Testing Frameworks

### Unit Testing with pytest

```python
# test_lambda_function.py
import json
import pytest
from lambda_function import lambda_handler

def test_lambda_handler_success():
    event = {
        'queryStringParameters': {
            'name': 'Test'
        }
    }
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'Test' in body['message']

def test_lambda_handler_no_name():
    event = {}
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'World' in body['message']

@pytest.fixture
def api_gateway_event():
    return {
        'httpMethod': 'GET',
        'queryStringParameters': {'name': 'Pytest'},
        'headers': {'Content-Type': 'application/json'}
    }

def test_with_fixture(api_gateway_event):
    response = lambda_handler(api_gateway_event, {})
    assert response['statusCode'] == 200
```

### Mocking AWS Services with moto

```python
import boto3
from moto import mock_s3
import pytest

@mock_s3
def test_s3_interaction():
    # Create mock S3 resource
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    
    # Test your Lambda function that uses S3
    from lambda_function import lambda_handler
    
    event = {
        'Records': [{
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'test.txt'}
            }
        }]
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
```

---

## Appendix E: Performance Optimization Checklist

### Code Optimization
- [ ] Initialize SDK clients outside handler (connection reuse)
- [ ] Use connection pooling for databases
- [ ] Minimize import statements
- [ ] Lazy load heavy dependencies
- [ ] Use async/await for concurrent operations
- [ ] Cache frequently accessed data
- [ ] Optimize data structures and algorithms

### Package Optimization
- [ ] Remove unnecessary dependencies
- [ ] Use Lambda Layers for large dependencies
- [ ] Minimize deployment package size
- [ ] Exclude tests and documentation from package
- [ ] Use compiled libraries when available

### Configuration Optimization
- [ ] Test different memory allocations
- [ ] Set appropriate timeout values
- [ ] Use provisioned concurrency for latency-sensitive functions
- [ ] Configure reserved concurrency for critical functions
- [ ] Enable X-Ray tracing selectively

### Architecture Optimization
- [ ] Use appropriate invocation type (sync vs async)
- [ ] Implement retry logic with exponential backoff
- [ ] Use SQS for decoupling and buffering
- [ ] Leverage Step Functions for complex workflows
- [ ] Consider Lambda@Edge for global distribution

---

## End of Labs

Thank you for completing the AWS Lambda Hands-On Lab! 

**Remember**: The best way to learn is by building. Start a project, experiment, and don't be afraid to make mistakes. The serverless community is here to help!

Kirk Patrick
