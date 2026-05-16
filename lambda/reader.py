import boto3
import json
import re
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

def lambda_handler(event, context):
    motor_id = event['queryStringParameters']['motor_id']
    date = event['queryStringParameters']['date']
    regex = "^\d{4}-\d{1,2}-\d{1,2}$"

    if(not re.match(regex, date)):
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps('Bad Request')
        }
    else:
        start = f"{date}T00:00:00Z"
        end = f"{date}T23:59:59Z"
        response = table.query(
            KeyConditionExpression=Key('motor_id').eq(motor_id) & Key('timestamp').between(start, end)
        )
        items = [item for item in response['Items'] if item['timestamp'] != 'CONFIG']

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(items, default=str)
        }