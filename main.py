import os
import requests
import boto3
import logging
from dotenv import load_dotenv
from json_log_formatter import JsonFormatter

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

def backup_workspaces(workspaces, TOKEN):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    s3 = boto3.client('s3')

    for workspace in workspaces:
        workspace_id = workspace['id']
        logger.info(f'Initiating backup for workspace with ID: {workspace_id}...')

        url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f'Failed to get current state version for workspace {workspace_id}.')
        else:
            logger.info(f'Got the current state version for workspace {workspace_id}')
            continue

def main():
    global logger
    logger = setup_logger()
    ORGANIZATION, S3_BUCKET, TOKEN = get_env_vars()
    workspaces = get_workspaces(ORGANIZATION, TOKEN)
    backup_workspaces(workspaces, TOKEN)

if __name__ == "__main__":
    load_dotenv()
    main()