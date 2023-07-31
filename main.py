import os
import requests
import boto3
import logging
from dotenv import load_dotenv
from json_log_formatter import JsonFormatter
import json
from datetime import datetime
import zipfile

def setup_logger():
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create handler
    handler = logging.StreamHandler()

    # Create formatter
    formatter = JsonFormatter()

    # Add formatter to handler
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Set level of logging
    logger.setLevel(logging.INFO)
    return logger

def get_env_vars():
    ORGANIZATION = os.getenv('ORGANIZATION')
    S3_BUCKET = os.getenv('S3_BUCKET')
    TOKEN = os.getenv('TOKEN')

    env_vars = {'ORGANIZATION': ORGANIZATION, 'S3_BUCKET': S3_BUCKET, 'TOKEN': TOKEN}
    missing_vars = [var for var, value in env_vars.items() if not value]

    if missing_vars:
        for var in missing_vars:
            logger.error(f'Environment variable {var} is not set.')
        exit(1)

    return ORGANIZATION, S3_BUCKET, TOKEN

def get_workspaces(ORGANIZATION, TOKEN):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    url = f'https://app.terraform.io/api/v2/organizations/{ORGANIZATION}/workspaces'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error('Failed to list workspaces.')
        exit(1)
    else:
        workspaces_data = response.json()['data']
        workspace_names = [workspace['attributes']['name'] for workspace in workspaces_data]
        logger.info(f'The workspaces are {workspace_names}')
    
    return workspaces_data

def get_download_url(workspaces, TOKEN):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    for workspace in workspaces:
        workspace_id = workspace['id']

        url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f'Failed to get current state version for workspace {workspace_id}.')
            continue

        state_download_url = response.json()["data"]["attributes"]["hosted-state-download-url"]
        logger.info(f'Got the current state version for workspace {workspace_id}. Proceeding with backup...')
        # logger.info(f'state download url {state_download_url}')
        return state_download_url 

def save_state_to_local_file(workspaces, state_download_url):
    for workspace in workspaces:
        workspace_id = workspace['id']

        filename = f'{workspace_id}.tfstate'
        state_response = requests.get(state_download_url)

        # Check if the request was successful
        if state_response.status_code != 200:
            logger.error(f'State file not found for workspace {workspace_id}.')
            continue  # Skip the current iteration and move to the next workspace

        with open(filename, 'w') as f:
            json.dump(state_response.json(), f)
        
        logger.info(f'Saved state file for workspace {workspace_id} as {filename}.')
        return filename

def zip_state_file(filename, workspaces):
    for workspace in workspaces:
        workspace_id = workspace['id']

        # Check if state file exists
        if not os.path.exists(filename):
            logger.error(f'State file {filename} not found for workspace {workspace_id}. No file to zip.')
            continue 

        zipname = f'{datetime.now().strftime("%s")}_{workspace_id}-backup.zip'
        with zipfile.ZipFile(zipname, 'w') as zipf:
            zipf.write(filename)
        logger.info(f'zip name {zipname}')
        return zipname

def format_s3_key(workspaces, ORGANIZATION):   
    for workspace in workspaces:
        workspace_id = workspace['id']

    timestamp = datetime.now().strftime("%s")
    s3_key = f'{datetime.now().strftime("%Y-%m-%d")}/terraform-{ORGANIZATION}/{timestamp}_{workspace_id}-backup.zip'
    logger.info(f's3-key {s3_key}')
    return s3_key

def upload_state_to_s3(S3_BUCKET, zipname, s3_key, filename):
    s3 = boto3.client('s3')
    s3.upload_file(zipname, S3_BUCKET, s3_key)
   
    os.remove(filename)
    os.remove(zipname)

def main():
    try:
        logging.info('Backup process started.')
        global logger
        logger = setup_logger()
        ORGANIZATION, S3_BUCKET, TOKEN = get_env_vars()
        workspaces = get_workspaces(ORGANIZATION, TOKEN)
        state_download_url = get_download_url(workspaces, TOKEN)
        filename = save_state_to_local_file(workspaces, state_download_url) 
        zipname = zip_state_file(filename, workspaces)
        s3_key = format_s3_key(workspaces, ORGANIZATION)
        upload_state_to_s3(S3_BUCKET, zipname, s3_key, filename)
    finally:
        exit(0)
        
if __name__ == "__main__":
    load_dotenv()
    
    main()