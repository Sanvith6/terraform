import json
import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    # S3 event gives bucket name and object key
    record = event["Records"][0]
    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    print(f"Bucket: {bucket_name}")
    print(f"Key: {object_key}")

    # Read file from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response["Body"].read().decode("utf-8")

    event_data = json.loads(file_content)

    print("Event data received:")
    print(event_data)

    return {
        "statusCode": 200,
        "body": "Event processed successfully"
    }
