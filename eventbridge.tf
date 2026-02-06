resource "aws_cloudwatch_event_rule" "daily_rule" {
  name                = "daily-summary-trigger"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "daily_lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_rule.name
  target_id = "daily-summary-lambda"
  arn       = aws_lambda_function.daily_report.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daily_report.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_rule.arn
}
