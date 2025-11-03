import json
import boto3

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        lista = [b["Name"] for b in response.get('Buckets', [])]
        return _resp(200, {"lista_buckets": lista})
    except Exception as e:
        return _resp(500, {"error": str(e)})

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }
