terraform {
  cloud {
    organization = "test-123454"

    workspaces {
       name = "test-1-workspace"
    }
  }
}

provider "aws" {
  region = var.region
}