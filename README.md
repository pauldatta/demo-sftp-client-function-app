# Demo SFTP Client Function App

This is a Python Azure Function App that allows you to perform various operations on files stored on an SFTP server. The supported operations include listing files on the SFTP server, getting file metadata and transferring to Azure Blob Storage.

## How to Use

To use this function app, you will need to deploy it to an Azure Function App instance and configure the required environment variables. Here are the steps to get started:

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Create an Azure Function App instance in the Azure Portal.
4. Deploy the function app to the Azure Function App instance using your preferred deployment method (e.g. Visual Studio Code, Azure CLI, etc.).
5. Configure the following environment variable in the Azure Function App instance:

   - `BlobStorageConnectionString`: The connection string for the Azure Blob Storage account for file copy from SFTP.

6. Test the function app by sending an HTTP request to the function app endpoint with the required parameters.

## Caveats

This function app is not intended for production use and should be used for testing and development purposes only. It is your responsibility to ensure that the function app is secure and that access to the SFTP server and Azure Blob Storage account is restricted to authorized users only. Additionally, this function app is not intended to be used as a replacement for a dedicated SFTP client or other secure file transfer solutions.

## Operations

The supported operations for this function app are:

1. `list_files_on_sftp`: This operation lists all files in the specified directory on the SFTP server. To call this operation, you need to send an HTTP POST request to the function app endpoint with the following parameters in the request body:

   - `username`: The username for the SFTP server.
   - `host`: The hostname or IP address of the SFTP server.
   - `private_key`: The private key for the SFTP server.
   - `operation`: The operation to perform (set to `list_files_on_sftp`).
   - `path`: The directory on the SFTP server to list files from.
   - `blob_storage_container_name`: Blank, not used for this operation.
   - `blob_storage_blob_name`: Blank, not used for this operation.

2. `get_file_metadata_on_sftp`: This operation gets the metadata for the specified file on the SFTP server. To call this operation, you need to send an HTTP POST request to the function app endpoint with the following parameters in the request body:

   - `username`: The username for the SFTP server.
   - `host`: The hostname or IP address of the SFTP server.
   - `private_key`: The private key for the SFTP server.
   - `operation`: The operation to perform (set to `get_file_metadata_on_sftp`).
   - `path`: The path to the file on the SFTP server to get metadata for.
   - `blob_storage_container_name`: Blank, not used for this operation.
   - `blob_storage_blob_name`: Blank, not used for this operation.

3. `download_file_from_sftp`: This operation downloads a file from the SFTP server and uploads it to Azure Blob Storage. The required parameters are:

   - `username`: The username for the SFTP server.
   - `host`: The hostname or IP address of the SFTP server.
   - `private_key`: The private key for the SFTP server, entire string.
   - `operation`: The operation to perform (set to `download_file_from_sftp`).
   - `sftp_path`: The path to the file on the SFTP server to download.
   - `blob_storage_container_name`: The name of the Azure Blob Storage container to use for SFTP file operations.
   - `blob_storage_blob_name`: The name of the Azure Blob Storage blob to use for SFTP file operations.


To call the API, you can use a tool like `curl` or an HTTP client like Postman to send an HTTP POST request to the function app endpoint with the required parameters in the request body. For example, to list files on the SFTP server, you can use the following `curl` command:

```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "myusername", "host": "mysftpserver.com", "private_key": "myprivatekey", "operation": "list_files_on_sftp", "path": "/mydirectory", "blob_storage_container_name": "", "blob_storage_blob_name": ""}' https://myfunctionapp.azurewebsites.net/api/http_trigger
```

Replace the values for username, host, private_key, path, blob_storage_container_name, and blob_storage_blob_name with your own values. 