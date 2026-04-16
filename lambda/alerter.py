import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

sns = boto3.client('sns', region_name='eu-north-1')

def lambda_handler(event, context):
    motor_id = event['motor_id']
    temperature = event['temperature']
    
    response = table.get_item(Key={'motor_id': motor_id, 'timestamp': 'CONFIG'})
    
    if 'Item' in response:
        threshold = response['Item']['temperature_threshold']
    else:
        threshold = 40
    
    if temperature > threshold:
        sns.publish(
            TopicArn="arn:aws:sns:eu-north-1:688567264451:motor-alerts",
            Message=f"Warning: Motor {motor_id} temperature {temperature}°C exceeds threshold {threshold}°C"
        )
        
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }