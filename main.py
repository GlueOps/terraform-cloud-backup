import os
import requests
import boto3
import logging
from dotenv import load_dotenv
from json_log_formatter import JsonFormatter
import json
from datetime import datetime
import zipfile
import smart_open
from typing import List

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

    try:
        response = requests.get(TERRAFORM_API_URL, headers=headers)
        response.raise_for_status() # Raise exception for 4xx and 5xx responses
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        exit(1)
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
        exit(1)
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
        exit(1)
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
        exit(1)

    workspaces_data = response.json()['data']
    workspace_with_states = []

    for workspace in workspaces_data:
        if get_state_download_url(workspace, TOKEN, log_errors=False): # Ignore workspaces without state files
            workspace_with_states.append(workspace)

    workspace_names = [workspace['attributes']['name'] for workspace in workspace_with_states] 
    logger.info(f'The workspaces with state files are {workspace_names}')
    
    return workspace_with_states

def get_state_download_url(workspace, TOKEN, log_errors=True):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    workspace_id = workspace['id']

    url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'
    response = requests.get(url, headers=headers)

    if response.ok:
        state_download_url = response.json()["data"]["attributes"]["hosted-state-download-url"]
        if log_errors:
            logger.info(f'Got the latest state file version for workspace {workspace_id}. Proceeding with backup...')
        return state_download_url
        
    else:
        if log_errors:
            logger.warning(f'No state file for workspace {workspace_id}.')
        return None

def format_s3_key(workspace, ORGANIZATION):   
    workspace_id = workspace['id']
    timestamp = datetime.utcnow().strftime("%s")
    s3_key = f'{datetime.utcnow().strftime("%Y-%m-%d")}/terraform-{ORGANIZATION}/{timestamp}_{workspace_id}-backup.zip'
    return s3_key

def save_state_to_remote_file(s3_key, workspace, state_download_url, S3_BUCKET, ORGANIZATION):
    workspace_id = workspace['id']
    state_response = requests.get(state_download_url)

    if state_response.ok:
        with smart_open.open(f's3://{S3_BUCKET}/{s3_key}', 'w') as f:
            json.dump(state_response.json(), f)

        logger.info(f'Saved state file for workspace {workspace_id} to {S3_BUCKET} with key {s3_key}.')
        return s3_key
    else:
        logger.error(f'State file not found for workspace {workspace_id}.')
        return None

def main():
    try:
        logging.info('Backup process started.')
        global logger
        logger = setup_logger()
        env_vars = get_env_vars()
        workspaces = get_workspaces(env_vars['ORGANIZATION'], env_vars['TOKEN'])
        for workspace in workspaces:
            logger.debug('Processing workspace %s', workspace['id'])  # Add debug log
            state_download_url = get_state_download_url(workspace, env_vars['TOKEN'])
            s3_key = format_s3_key(workspace, env_vars['ORGANIZATION'])
            if state_download_url:
                logger.debug('State file found for workspace %s', workspace['id'])  # Add debug log
                filename = save_state_to_remote_file(s3_key, workspace, state_download_url, env_vars['S3_BUCKET'], env_vars['ORGANIZATION'])
    except Exception as e:  # Catch any exceptions
        logger.exception('An error occurred: %s', e)  # Log the exception
    finally:
        exit(0)


if __name__ == "__main__":
    load_dotenv()
    main()