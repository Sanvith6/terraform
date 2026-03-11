resource "aws_s3_object" "seed_event_login" {
  count = var.enable_seed_upload ? 1 : 0

  bucket       = aws_s3_bucket.s3_bucket.id
  key          = "events/event-login.json"
  source       = "${path.module}/sample_data/event-login.json"
  etag         = filemd5("${path.module}/sample_data/event-login.json")
  content_type = "application/json"

  # Ensure notifications are configured before uploading seed objects.
  depends_on = [aws_s3_bucket_notification.s3_trigger]
}

resource "aws_s3_object" "seed_event_logout" {
  count = var.enable_seed_upload ? 1 : 0

  bucket       = aws_s3_bucket.s3_bucket.id
  key          = "events/event-logout.json"
  source       = "${path.module}/sample_data/event-logout.json"
  etag         = filemd5("${path.module}/sample_data/event-logout.json")
  content_type = "application/json"

  # Ensure notifications are configured before uploading seed objects.
  depends_on = [aws_s3_bucket_notification.s3_trigger]
}

