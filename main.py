import io
import json
import os
from datetime import datetime
from zipfile import ZipFile

import requests
import smart_open
from glueops.setup_logging import configure as go_configure_logging


#=== configure logging
logger = go_configure_logging(
    name='TERRAFORM_CLOUD_BACKUP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

# retrieve environment configuration
try:
    ORGANIZATION = os.environ['ORGANIZATION']
    S3_BUCKET = os.environ['S3_BUCKET']
    TOKEN = os.environ['TOKEN']
except KeyError:
    logger.exception('failed to retrieve environment configuration')
    raise

# create headers
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/vnd.api+json'
}


def get_workspaces(ORGANIZATION):
    TERRAFORM_API_URL = f'https://app.terraform.io/api/v2/organizations/{ORGANIZATION}/workspaces'

    try:
        response = requests.get(TERRAFORM_API_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception:
        logger.exception(f"request exception")
        raise

    workspaces_data = response.json()['data']

    workspace_with_states = [
        workspace for workspace in workspaces_data
        if get_state_download_url(workspace)
    ]

    workspace_names = [workspace['attributes']['name'] for workspace in workspace_with_states] 
    logger.info(f'The workspaces with state files are {workspace_names}')
    
    return workspace_with_states


def get_state_download_url(workspace):
    workspace_id = workspace['id']

    url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except Exception:
        logger.exception(f'Failed to retrieve current state metadata for: {workspace}')

    try:
        state_download_url = response.json()["data"]["attributes"]["hosted-state-download-url"]
        logger.info(f'retrieved download_url for: {workspace}')
        return state_download_url
    except KeyError:
        logger.warning(f'no state file download_url for {workspace}')
        return None


def format_s3_key(workspace, ORGANIZATION):   
    workspace_id = workspace['id']
    workspace_name = workspace['attributes']['name']
    timestamp = datetime.utcnow().strftime("%s")
    s3_key = f'terraform_cloud/{datetime.utcnow().strftime("%Y-%m-%d")}/terraform-{ORGANIZATION}/{timestamp}_{workspace_name}_{workspace_id}-backup.zip'
    return s3_key


def save_state_to_remote_file(s3_key, workspace, state_download_url, S3_BUCKET):
    workspace_id = workspace['id']
    state_response = requests.get(state_download_url, headers=HEADERS)

    if state_response.ok:
        # Create a ZipFile object in memory
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zipf:
            # Name of the file inside the ZIP archive
            zip_file_name = f'{workspace_id}.tfstate'
            
            # Write the state file into the ZIP archive
            zipf.writestr(zip_file_name, json.dumps(state_response.json()))

        # Write the ZIP archive to S3
        zip_buffer.seek(0) # Rewind the buffer to the beginning
        with smart_open.open(f's3://{S3_BUCKET}/{s3_key}', 'wb') as f:
            f.write(zip_buffer.read())

        return s3_key
    else:
        logger.exception(f'workspace: {workspace_id} - Unable to save state file to s3 .  response: {state_response}')
        return None


def main():
    try:
        logger.info('Backup process started.')
        workspaces = get_workspaces(ORGANIZATION)
        for workspace in workspaces:
            logger.debug(f'Processing workspace: {workspace["id"]} - {workspace["attributes"]["name"]}')
            state_download_url = get_state_download_url(workspace)
            if state_download_url:
                logger.debug(f'State file found for workspace  {workspace["id"]} - {workspace["attributes"]["name"]}')
                s3_key = format_s3_key(workspace, ORGANIZATION)
                save_state_to_remote_file(s3_key, workspace, state_download_url, S3_BUCKET)
                logger.info(f'wrote state file for {workspace["id"]}, {workspace["attributes"]["name"]} to s3://{S3_BUCKET}/{s3_key}')
    except Exception as e:
        logger.exception(f'An error occurred: {e}')
        raise
        
if __name__ == "__main__":
    main()
