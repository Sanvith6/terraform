import boto3
import json
from datetime import date

s3 = boto3.client("s3")

BUCKET_NAME = "task-bucket-2026"
PREFIX = "events/"

def lambda_handler(event, context):
    today = date.today().isoformat()
    event_count = 0
    event_types = {}

    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PREFIX
    )

    if "Contents" in response:
        for obj in response["Contents"]:
            file = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
            content = json.loads(file["Body"].read().decode("utf-8"))

            event_count += 1
            etype = content.get("event_type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1

    print("===== DAILY EVENT SUMMARY =====")
    print(f"Date: {today}")
    print(f"Total events: {event_count}")
    print("Event breakdown:")

    for k, v in event_types.items():
        print(f"{k}: {v}")

    return {
        "statusCode": 200,
        "body": "Daily summary generated"
    }
