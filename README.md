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
```python
$ docker run --env-file .env -t ghcr.io/glueops/terraform-cloud-backup:feature-tfc-backup
```
