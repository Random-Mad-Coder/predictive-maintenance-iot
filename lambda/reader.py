import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

def lambda_handler(event, context):
    motor_id = event['queryStringParameters']['motor_id']
    response = table.query(KeyConditionExpression=Key('motor_id').eq(motor_id))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response['Items'], default=str)
    }