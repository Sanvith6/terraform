resource "aws_s3_bucket" "s3_bucket" {
  bucket = "task-bucket-2026"

  tags = {
    Name        = "task-bucket"
    Environment = "dev"
    Project     = "event-driven-pipeline"
  }
}

resource "aws_s3_bucket_versioning" "s3_bucket_versioning" {
  bucket = aws_s3_bucket.s3_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_notification" "s3_trigger" {
  bucket = aws_s3_bucket.s3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.event_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "events/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
