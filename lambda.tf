resource "aws_lambda_function" "event_processor" {
  function_name = "s3-event-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "processor.lambda_handler"
  runtime       = "python3.9"

  filename         = "${path.module}/lambda/processor.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/processor.zip")

  timeout = 10
}
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.event_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.s3_bucket.arn
}
resource "aws_lambda_function" "daily_report" {
  function_name = "daily-summary-report"
  role          = aws_iam_role.lambda_role.arn
  handler       = "daily_report.lambda_handler"
  runtime       = "python3.9"

  filename         = "${path.module}/lambda/daily_report.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/daily_report.zip")

  timeout = 15
}
