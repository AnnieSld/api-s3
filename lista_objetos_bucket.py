import json
import boto3

def lambda_handler(event, context):
    # Entrada (json)
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body or '{}')
        elif body is None:
            body = {}
        nombre_bucket = body.get('bucket')
        if not nombre_bucket:
            return _resp(400, {"error": "Falta 'bucket' en el body"})

        # Proceso
        s3 = boto3.client('s3')
        resp = s3.list_objects_v2(Bucket=nombre_bucket)
        lista = [obj['Key'] for obj in resp.get('Contents', [])]

        return _resp(200, {
            "bucket": nombre_bucket,
            "lista_objetos": lista
        })
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
