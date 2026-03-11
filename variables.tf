variable "bucket_name" {
  description = "Globally unique S3 bucket name for event files"
  type        = string
  default     = "task-bucket-2026"
}

variable "enable_seed_upload" {
  description = "Upload sample event files to events/ during terraform apply"
  type        = bool
  default     = true
}
