import azure.functions as func
import logging
import os
import io
import tempfile
import pysftp
import paramiko
import json
import sftp
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        # Get the request body
        req_body = req.get_json()

        # Get the SFTP credentials from the request body
        username = req_body.get('username')
        host = req_body.get('host')
        private_key = req_body.get('private_key')

        # Get the operation to perform from the request body
        operation = req_body.get('operation')

        # Get the path to the Azure Blob Storage container and blob for SFTP file operations
        blob_storage_conn_str = os.environ['BlobStorageConnectionString']
        blob_storage_container_name = req_body.get('blob_storage_container_name')
        blob_storage_blob_name = req_body.get('blob_storage_blob_name')

        logging.info(f"username: {username}, host: {host}, operation: {operation}, blob_storage_container_name: {blob_storage_container_name}, blob_storage_blob_name: {blob_storage_blob_name}")
        
        # Perform the requested operation
        if operation == 'list_files_on_sftp':
            files = list_files_on_sftp(req_body, host, username, private_key)
            return func.HttpResponse(json.dumps(files), mimetype="application/json")

        elif operation == 'get_file_metadata_on_sftp':
            file_metadata = get_file_metadata_on_sftp(req_body, host, username, private_key)
            return func.HttpResponse(
                json.dumps(file_metadata),
                status_code=file_metadata['status_code'],
                mimetype="application/json"
            )

        elif operation == 'download_file_from_sftp':
            if not all(param in req_body for param in ['sftp_path', 'blob_storage_container_name', 'blob_storage_blob_name']):
                return func.HttpResponse("Missing required parameters", status_code=400)
            result = download_file_from_sftp(req_body, host, username, private_key, blob_storage_conn_str, blob_storage_container_name, blob_storage_blob_name)
            return func.HttpResponse(
                json.dumps(result),
                status_code=result['status_code'],
                mimetype="application/json"
            )
        # elif operation == 'upload_file_to_sftp':
        else:
            return func.HttpResponse(
                "Invalid operation",
                status_code=400
            )
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            "An error occurred",
            status_code=500
        )

def list_files_on_sftp(req_body, host, username, private_key):
    path = req_body.get('path')
    logging.info(f"Inside list_files_on_sftp, received path: {path}")

    # Connect to the SFTP server using the private key
    ssh = sftp.connect_to_sftp(host, username, private_key)

    # Open an SFTP session and list the files in the specified path
    sftp_client = ssh.open_sftp()
    files = sftp_client.listdir()

    # Close the SFTP session and SSH connection
    sftp_client.close()
    ssh.close()

    # Return the list of files
    return files

def get_file_metadata_on_sftp(req_body, host, username, private_key):
    path = req_body.get('path')
    logging.info(f"Inside get_file_metadata_on_sftp, received path: {path}")

    try:
        # Connect to the SFTP server using the private key
        ssh = sftp.connect_to_sftp(host, username, private_key)

        # Open an SFTP session and get the file attributes for the specified path
        sftp_client = ssh.open_sftp()
        file_attr = sftp_client.stat(path)

        # Close the SFTP session and SSH connection
        sftp_client.close()
        ssh.close()

        # Return the file attributes as a dictionary
        return {
            'filename': os.path.basename(path),
            'size': file_attr.st_size,
            'last_modified': file_attr.st_mtime,
            'status_code': '200'
        }
    except FileNotFoundError:
        # Return a 404 Not Found error if the specified file is not found on the SFTP server
        return {
            'error': "File not found on SFTP server",
            'status_code': '404'
        }

def download_file_from_sftp(req_body, host, username, private_key, blob_storage_conn_str, blob_storage_container_name, blob_storage_blob_name):
    # Get the path to the file on the SFTP server from the request body
    sftp_path = req_body.get('sftp_path')

    # Connect to the SFTP server using the private key
    ssh = sftp.connect_to_sftp(host, username, private_key)

    try:
        # Open an SFTP session and download the file to a temporary directory
        sftp_client = ssh.open_sftp()
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, os.path.basename(sftp_path))
            sftp_client.get(sftp_path, local_path)

            # Upload the file to Azure Blob Storage
            blob_service_client = BlobServiceClient.from_connection_string(blob_storage_conn_str)
            container_client = blob_service_client.get_container_client(blob_storage_container_name)
            blob_client = container_client.get_blob_client(blob_storage_blob_name)
            if not blob_client.exists():
                with open(local_path, "rb") as data:
                    blob_client.upload_blob(data)

        # Close the SFTP session and SSH connection
        sftp_client.close()
        ssh.close()

        # Return a JSON object with a message indicating that the file was downloaded from SFTP and uploaded to Azure Blob Storage
        return {
            'message': f"File downloaded from SFTP and uploaded to Azure Blob Storage: {sftp_path}",
            'blob_url': blob_client.url,
            'status_code': '200'
        }
    except FileNotFoundError:
        return {
            'error': "File not found on SFTP server",
            'status_code': '404'
        }