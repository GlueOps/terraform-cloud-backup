variable "bucket-name" {
  default     = "flakyc00ki3s"
  type        = string
  description = "the s3 bucket name"
}

variable "tag-name" {
  default     = "test"
  type        = string
  description = "tag name to identify resource easily"
}

variable "tag-env" {
  default     = "test-env"
  type        = string
  description = "specify the environment to tag the resurces by"
}