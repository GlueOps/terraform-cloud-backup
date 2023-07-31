terraform {
  cloud {
    organization = "test-123454"

    workspaces {
      name = "terraform-cloud-backup"
    }
  }
}

provider "aws" {
  region = var.region
}