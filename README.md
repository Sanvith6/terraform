# Event-Driven AWS Pipeline with Terraform

This project provisions an AWS event-processing pipeline using Terraform.

It creates:
- An S3 bucket for incoming event JSON files
- A Lambda function triggered when new files are uploaded under `events/`
- A second Lambda function that generates a daily summary
- An EventBridge schedule that runs the summary Lambda every day
- IAM role and policies required for Lambda + S3 access
- Seed event object uploads for zero-manual setup

## Architecture

1. JSON event files are uploaded to `s3://<your-bucket-name>/events/...`
2. S3 sends an object-created event to `s3-event-processor` Lambda
3. `s3-event-processor` reads and logs event content
4. EventBridge rule (`rate(1 day)`) invokes `daily-summary-report` Lambda
5. `daily-summary-report` scans objects under `events/` and logs event counts by `event_type`

## End-to-End Pipeline

```mermaid
flowchart LR
    A[Developer Push/PR to GitHub] --> B[GitHub Actions Terraform CI]
    B --> B1[terraform init]
    B1 --> B2[terraform validate]
    B2 --> B3[terraform plan]
    B3 --> C[python deploy.py]

    C --> D[Provision AWS Infrastructure]
    D --> D1[S3 bucket from Terraform var bucket_name]
    D --> D2[Lambda s3-event-processor]
    D --> D3[Lambda daily-summary-report]
    D --> D4[EventBridge daily rule]
    D --> D5[IAM role and policies]
    D --> D6[Seed uploads to events/]

    D6 --> E[S3 ObjectCreated Event]
    E --> F[s3-event-processor Lambda]
    F --> G[Reads object JSON and logs event data]

    D4 --> H[Daily schedule rate(1 day)]
    H --> I[daily-summary-report Lambda]
    I --> J[List/read objects under events/]
    J --> K[Count by event_type and log summary]
```

## Repository Structure

```text
.
|-- deploy.py                # Packages Lambda zip files and runs Terraform deploy
|-- provider.tf              # AWS provider (us-east-1)
|-- terraform.tf             # Terraform + provider version constraints
|-- variables.tf             # Input variables (bucket name, seed upload toggle)
|-- s3.tf                    # S3 bucket, versioning, and S3->Lambda notification
|-- iam.tf                   # Lambda IAM role + policies
|-- lambda.tf                # Lambda resources (processor + daily report)
|-- eventbridge.tf           # Scheduled EventBridge rule + target + permission
|-- seed_data.tf             # Auto-upload sample event files to events/ prefix
|-- lambda/
|   |-- processor.py
|   |-- processor.zip
|   |-- daily_report.py
|   `-- daily_report.zip
`-- sample_data/
    |-- event-login.json
    `-- event-logout.json
```

## Prerequisites

- Terraform `>= 1.0`
- Python `>= 3.9`
- AWS account with permissions for S3, Lambda, IAM, EventBridge, CloudWatch Logs
- AWS credentials configured locally

## AWS Region and Naming

- Region is `us-east-1` in `provider.tf`.
- S3 bucket name comes from Terraform variable `bucket_name`.

## Deploy

From the project root:

```powershell
python .\deploy.py
```

This script:
- Packages Lambda source into zip artifacts
- Generates a unique bucket name (unless `--bucket-name` is passed)
- Runs `terraform init`, `terraform plan`, and `terraform apply -auto-approve`

Optional flags:

```powershell
python .\deploy.py --skip-apply
python .\deploy.py --bucket-name my-unique-event-bucket-2026
python .\deploy.py --no-auto-approve
```

## Test the Pipeline

1. `terraform apply` auto-uploads seed files to `events/`
2. Verify `/aws/lambda/s3-event-processor` logs in CloudWatch
3. Verify `/aws/lambda/daily-summary-report` logs in CloudWatch

Manual invoke example:

```powershell
aws lambda invoke --function-name daily-summary-report --payload "{}" out.json
Get-Content .\out.json
```

## Notes and Current Limitations

- `daily_report.py` reads only first page from `list_objects_v2` (up to 1000 keys)
- `daily_report.py` reads `BUCKET_NAME` from Lambda environment variables
- Seed upload can be disabled with `-var "enable_seed_upload=false"`
- Runtime is `python3.9` in Terraform

## Destroy Infrastructure

```powershell
aws s3 rm s3://<your-bucket-name> --recursive
terraform destroy
```

## License

This repository includes an MIT license in `LICENSE`.
