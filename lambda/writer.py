import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('motor-metrics')

def lambda_handler(event, context):
    item = json.loads(json.dumps(event), parse_float=Decimal)
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }