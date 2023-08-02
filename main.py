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
    logger = logging.getLogger('TerraformBackupScript')

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger

def get_env_vars():
    env_vars = {
        'ORGANIZATION': os.getenv('ORGANIZATION'),
        'S3_BUCKET': os.getenv('S3_BUCKET'),
        'TOKEN': os.getenv('TOKEN')
    }
    
    missing_vars = [var for var, value in env_vars.items() if not value]

    if missing_vars:
        for var in missing_vars:
            logger.error(f'Environment variable {var} is not set.')
        exit(1)

    return env_vars

def get_workspaces(ORGANIZATION, TOKEN):
    TERRAFORM_API_URL = f'https://app.terraform.io/api/v2/organizations/{ORGANIZATION}/workspaces'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    response = requests.get(TERRAFORM_API_URL, headers=headers)

    if not response.ok:
        logger.error('Failed to list workspaces.')
        exit(1)
    else:
        workspaces_data = response.json()['data']
        workspace_names = [workspace['attributes']['name'] for workspace in workspaces_data]
        logger.info(f'The workspaces are {workspace_names}')
    
    return workspaces_data

def get_state_download_url(workspace, TOKEN):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    workspace_id = workspace['id']

    url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'
    response = requests.get(url, headers=headers)

    if response.ok:
        state_download_url = response.json()["data"]["attributes"]["hosted-state-download-url"]
        logger.info(f'Got the latest state file version for workspace {workspace_id}. Proceeding with backup...')
        return state_download_url
        
    else:
        logger.error(f'Failed to get latest state file version for workspace {workspace_id}.')
        return None

def save_state_to_local_file(workspace, state_download_url):
    workspace_id = workspace['id']
    filename = f'{workspace_id}.tfstate'
    state_response = requests.get(state_download_url)

    if state_response.ok:
        with open(filename, 'w') as f:
            json.dump(state_response.json(), f)

        logger.info(f'Saved state file for workspace {workspace_id} as {filename}.')
        return filename
    else:
        logger.error(f'State file not found for workspace {workspace_id}.')
        return None

def zip_state_file(filename, workspace):
    workspace_id = workspace['id']

    if os.path.exists(filename):
        zipname = f'{datetime.now().strftime("%s")}_{workspace_id}-backup.zip'
        with zipfile.ZipFile(zipname, 'w') as zipf:
            zipf.write(filename)
        logger.info(f'State file is zipped and stored as {zipname}')
        return zipname
    else:
        logger.error(f'State file not found for workspace {workspace_id}. No file to zip.')
        return None

def format_s3_key(workspace, ORGANIZATION):   
    workspace_id = workspace['id']
    timestamp = datetime.utcnow().strftime("%s")
    s3_key = f'{datetime.utcnow().strftime("%Y-%m-%d")}/terraform-{ORGANIZATION}/{timestamp}_{workspace_id}-backup.zip'
    return s3_key

def upload_state_to_s3(S3_BUCKET, zipname, s3_key, filename):
    s3 = boto3.client('s3')
    s3.upload_file(zipname, S3_BUCKET, s3_key)
    logger.info(f'Uploaded state file to S3 bucket {S3_BUCKET} with key {s3_key}')

    os.remove(filename)
    os.remove(zipname)

def main():
    try:
        logging.info('Backup process started.')
        global logger
        logger = setup_logger()
        env_vars = get_env_vars()
        workspaces = get_workspaces(env_vars['ORGANIZATION'], env_vars['TOKEN'])
        for workspace in workspaces:
            state_download_url = get_state_download_url(workspace, env_vars['TOKEN'])
            if state_download_url:
                filename = save_state_to_local_file(workspace, state_download_url)
                if filename:
                    zipname = zip_state_file(filename, workspace)
                    if zipname:
                        s3_key = format_s3_key(workspace, env_vars['ORGANIZATION'])
                        upload_state_to_s3(env_vars['S3_BUCKET'], zipname, s3_key, filename)
    finally:
        exit(0)

if __name__ == "__main__":
    load_dotenv()
    main()