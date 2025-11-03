# tarea_s3.py
import os, json, base64, boto3, botocore

s3 = boto3.client("s3")
STAGE = os.getenv("STAGE", "dev")

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, ensure_ascii=False)
    }

def crear_bucket(event, context):
    # Body: { "name": "catalogo-productos" }
    try:
        body = json.loads(event.get("body") or "{}")
        base = body.get("name")
        if not base:
            return _resp(400, {"error": "name es requerido"})
        bucket = f"{base}-{STAGE}"
        region = os.environ.get("AWS_REGION", "us-east-1")
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket)
        else:
            s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region})
        return _resp(200, {"message": "bucket creado", "bucket": bucket})
    except botocore.exceptions.ClientError as e:
        return _resp(400, {"error": str(e)})
    except Exception as e:
        return _resp(500, {"error": str(e)})

def crear_directorio(event, context):
    # Body: { "bucket": "catalogo-productos-dev", "prefix": "imagenes/" }
    try:
        body = json.loads(event.get("body") or "{}")
        bucket = body.get("bucket")
        prefix = body.get("prefix")
        if not bucket or not prefix:
            return _resp(400, {"error": "bucket y prefix son requeridos"})
        if not prefix.endswith("/"):
            prefix += "/"
        s3.put_object(Bucket=bucket, Key=prefix, Body=b"")
        return _resp(200, {"message": "directorio creado", "bucket": bucket, "prefix": prefix})
    except botocore.exceptions.ClientError as e:
        return _resp(400, {"error": str(e)})
    except Exception as e:
        return _resp(500, {"error": str(e)})

def subir_archivo(event, context):
    # Body: { "bucket":"...","prefix":"imagenes/","filename":"pollo.jpg","fileBase64":"<BASE64>" }
    try:
        body = json.loads(event.get("body") or "{}")
        bucket = body.get("bucket")
        prefix = (body.get("prefix") or "")
        filename = body.get("filename")
        file_b64 = body.get("fileBase64")
        if not all([bucket, filename, file_b64]):
            return _resp(400, {"error": "bucket, filename y fileBase64 son requeridos"})

        if prefix and not prefix.endswith("/"):
            prefix += "/"
        key = f"{prefix}{filename}"
        data = base64.b64decode(file_b64)

        extra = {}
        low = filename.lower()
        if low.endswith((".jpg",".jpeg")): extra["ContentType"]="image/jpeg"
        elif low.endswith(".png"): extra["ContentType"]="image/png"

        s3.put_object(Bucket=bucket, Key=key, Body=data, **extra)
        return _resp(200, {"message":"archivo subido","bucket":bucket,"key":key,"size":len(data)})
    except botocore.exceptions.ClientError as e:
        return _resp(400, {"error": str(e)})
    except Exception as e:
        return _resp(500, {"error": str(e)})
