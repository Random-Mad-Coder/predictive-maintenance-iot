import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def lambda_handler(event, context):
    method = event['requestContext']['http']['method']

    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }

    motor_id = event['queryStringParameters']['motor_id']

    if method == 'GET':
        response = table.get_item(Key={'motor_id': motor_id, 'timestamp': 'CONFIG'})
        if 'Item' in response:
            item = response['Item']
            item['temperature_threshold'] = float(item['temperature_threshold'])
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps(item)
            }
        else:
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'temperature_threshold': 40})
            }

    elif method == 'PUT':
        body = json.loads(event['body'], parse_float=Decimal)
        body.update({'motor_id': motor_id, 'timestamp': 'CONFIG'})
        table.put_item(Item=body)
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps('OK')
        }