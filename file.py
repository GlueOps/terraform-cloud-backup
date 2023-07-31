import os
import requests
import boto3
from datetime import datetime
import zipfile
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get environment variables
ORGANIZATION = os.getenv('ORGANIZATION')
S3_BUCKET = os.getenv('S3_BUCKET')
TOKEN = os.getenv('TOKEN')

if not all([ORGANIZATION, S3_BUCKET, TOKEN]):
    logging.error('One or more environment variables are not set.')
    exit(1)

# Headers for the API calls
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/vnd.api+json'
}

# Get list of workspaces
url = f'https://app.terraform.io/api/v2/organizations/{ORGANIZATION}/workspaces'
response = requests.get(url, headers=headers)

if response.status_code != 200:
    logging.error('Failed to list workspaces.')
    exit(1)

workspaces = response.json()['data']

s3 = boto3.client('s3')

for workspace in workspaces:
    workspace_id = workspace['id']
    logging.info(f'Backing up workspace: {workspace_id}')

    # Get the current state version for the workspace
    url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f'Failed to get current state version for workspace {workspace_id}.')
        continue

    # Get the download url from the response
    download_url = response.json()['data']['attributes']['hosted-state-download-url']

    # Download the state
    state_response = requests.get(download_url)

    if state_response.status_code != 200:
        logging.error(f'Failed to download state for workspace {workspace_id}.')
        continue

    # Save the state to a local file
    filename = f'{workspace_id}.tfstate'
    with open(filename, 'w') as f:
        json.dump(state_response.json(), f)

    # Zip the file
    zipname = f'{datetime.now().strftime("%s")}_{workspace_id}-backup.zip'
    with zipfile.ZipFile(zipname, 'w') as zipf:
        zipf.write(filename)

    # Format the S3 key as per requirement
    s3_key = f'{datetime.now().strftime("%Y-%m-%d")}/terraform-{ORGANIZATION}/{zipname}'

    # Upload to S3
    s3.upload_file(zipname, S3_BUCKET, s3_key)

    # Remove local state and zip files
    os.remove(filename)
    os.remove(zipname)

logging.info('Backup process completed.')
exit(0)
