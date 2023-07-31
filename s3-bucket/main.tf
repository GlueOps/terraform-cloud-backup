resource "aws_s3_bucket" "storage-s3" {
  bucket = var.bucket-name

  tags = {
    Name        = var.tag-name
    Environment = var.tag-env
  }
}