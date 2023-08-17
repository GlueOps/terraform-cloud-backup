# terraform-cloud-backup
This repository creates a backup of all terraform cloud state files, to prevent file loss in case of accidental deletion of a terraform workspace.

The workspace is setup to run the ```CLI Driven workflow```. 

## Running the script

- Generate your AWS tokens ```AWS_ACCESS_KEY_ID```, ```AWS_SECRET_ACCESS_KEY``` and ```AWS_DEFAULT_REGION``` and add them to your Terraform Workspace

- Create a ```.env``` file, with the following contents
```bash
ORGANIZATION=<some-value>
S3_BUCKET=<some-value>
TOKEN=<some-value>
AWS_ACCESS_KEY_ID=<some-value>
AWS_SECRET_ACCESS_KEY=<some-value>
AWS_DEFAULT_REGION=<some-value>
```

- Runing the script
```sh
$ docker run --env-file .env ghcr.io/glueops/terraform-cloud-backup:main
```

## Restoring a state
- Delete any existing terraform configuration (in your working directory)
- Locate the S3 bucket, download and then unzip the state file.
- Place the unzipped state file in the current working directory (where terraform configuration files are)
- Edit the ```provider.tf``` file to (remove the ```terraform cloud``` configuration)
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
}
```

- Run the following commands:
```bash
$ terraform init -reconfigure
$ terraform state push <unzipped-state-file>.tfstate
$ terraform plan
```

Check the plan output to track the state of your configuration.
**Remember to edit the ```provier.tf``` file, to use ```terraform cloud```**