# terraform-cloud-backup
This repository creates a backup of all terraform cloud state files, to prevent file loss in case of accidental deletion of a terraform workspace.

The workspace is setup to run the ```CLI Driven workflow```. 

## Running the script

- Generate your AWS tokens ```AWS_ACCESS_KEY_ID``` and ```AWS_SECRET_ACCESS_KEY``` and add them to your Terraform Workspace

- Ensure your file ```~/.aws/credentials``` is in this format (remove trailing spaces or symbols)
```
[profile-name or default]
aws_access_key_id = <some-value>
aws_secret_access_key = <some-value>
```

- Generate a Terraform token
```bash
$ terraform login
```

- Create terraform resources
```bash
$ terraform init
$ terraform fmt
$ terraform validate
$ terraform plan
$ terraform apply
```

- Create a ```.env``` file, with the following contents
```bash
ORGANIZATION=<some-value>
S3_BUCKET=<some-value>
TOKEN=<some-value>
```

- Runing the script
```python
$ python main.py
```
