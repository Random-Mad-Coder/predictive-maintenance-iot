import boto3
import json
import re
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

def return_success(response):
    items = [item for item in response['Items'] if item['timestamp'] != 'CONFIG']

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(items, default=str)
    }

def return_bad_request():
    return {
        'statusCode': 400,
        'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps('Bad Request')
    }


def lambda_handler(event, context):
    params = event.get('queryStringParameters') or {}
    motor_id = params.get('motor_id')

    if not motor_id:
        return return_bad_request()
    
    date = params.get('date')

    if date:
        regex = "^\d{4}-\d{2}-\d{2}$"

        if(not re.match(regex, date)):
            return return_bad_request()
    
        else:
            start = f"{date}T00:00:00Z"
            end = f"{date}T23:59:59Z"
            response = table.query(KeyConditionExpression=Key('motor_id').eq(motor_id) & Key('timestamp').between(start, end))
            return return_success(response)
    else:
        response = table.query(KeyConditionExpression=Key('motor_id').eq(motor_id))
        return return_success(response)