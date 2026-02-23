# Event-Driven AWS Pipeline with Terraform

This project provisions an AWS event-processing pipeline using Terraform.

It creates:
- An S3 bucket for incoming event JSON files
- A Lambda function triggered when new files are uploaded under `events/`
- A second Lambda function that generates a daily summary
- An EventBridge schedule that runs the summary Lambda every day
- IAM role and policies required for Lambda + S3 access

## Architecture

1. JSON event files are uploaded to `s3://task-bucket-2026/events/...`
2. S3 sends an object-created event to `s3-event-processor` Lambda
3. `s3-event-processor` reads and logs event content
4. EventBridge rule (`rate(1 day)`) invokes `daily-summary-report` Lambda
5. `daily-summary-report` scans objects under `events/` and logs event counts by `event_type`

## Repository Structure

```text
.
|-- provider.tf              # AWS provider (us-east-1)
|-- terraform.tf             # Terraform + provider version constraints
|-- s3.tf                    # S3 bucket, versioning, and S3->Lambda notification
|-- iam.tf                   # Lambda IAM role + policies
|-- lambda.tf                # Lambda resources (processor + daily report)
|-- eventbridge.tf           # Scheduled EventBridge rule + target + permission
|-- lambda/
|   |-- processor.py
|   |-- processor.zip
|   |-- daily_report.py
|   `-- daily_report.zip
`-- sample_data/
    `-- event-login.json
```

## Prerequisites

- Terraform `>= 1.0` (recommended latest stable)
- AWS account with permissions for:
  - S3
  - Lambda
  - IAM
  - EventBridge (CloudWatch Events)
- AWS credentials configured locally (for example via AWS CLI profile or environment variables)

## AWS Region and Naming

- Region is currently hardcoded to `us-east-1` in `provider.tf`.
- S3 bucket name is hardcoded to `task-bucket-2026` in `s3.tf` and `iam.tf`.

Important:
- S3 bucket names are globally unique. If this name already exists, `terraform apply` will fail.
- If you rename the bucket, update all references consistently:
  - `s3.tf`
  - `iam.tf`
  - `lambda/daily_report.py` (`BUCKET_NAME`)

## Deploy

From the project root:

```powershell
terraform init
terraform plan
terraform apply
```

Confirm with `yes` when prompted.

## Lambda Packaging

Terraform deploys Lambda code from:
- `lambda/processor.zip`
- `lambda/daily_report.zip`

If you change Python files, rebuild ZIPs before `terraform apply`.

Example (PowerShell, from project root):

```powershell
Compress-Archive -Path .\lambda\processor.py -DestinationPath .\lambda\processor.zip -Force
Compress-Archive -Path .\lambda\daily_report.py -DestinationPath .\lambda\daily_report.zip -Force
terraform apply
```

## Test the Pipeline

1. Upload a valid event file to S3 under the `events/` prefix.
2. Verify processor Lambda logs in CloudWatch.
3. Trigger daily report Lambda manually (or wait for schedule) and verify summary logs.

Upload example:

```powershell
aws s3 cp .\sample_data\event-login.json s3://task-bucket-2026/events/event-login.json
```

Manual invoke example:

```powershell
aws lambda invoke --function-name daily-summary-report --payload "{}" out.json
Get-Content .\out.json
```

## Event JSON Format

Expected fields (as used by current Lambda logic):

```json
{
  "event_id": "evt-1001",
  "user_id": "user-42",
  "event_type": "login",
  "source": "web_app",
  "timestamp": "2026-02-05T10:15:30Z"
}
```

## Notes and Current Limitations

- `daily_report.py` reads only the first page of `list_objects_v2` results (up to 1000 keys).
- `daily_report.py` has `BUCKET_NAME` hardcoded; it is not injected from Terraform.
- `sample_data/event-login.json` currently contains two JSON objects in one file; upload one valid JSON object per file for reliable processing.
- Runtime is fixed to `python3.9` in Terraform.

## Destroy Infrastructure

```powershell
terraform destroy
```

Note:
- If the bucket is not empty, destroy may fail. Delete objects first:

```powershell
aws s3 rm s3://task-bucket-2026 --recursive
terraform destroy
```

## License

This repository includes an MIT license in `LICENSE`.

