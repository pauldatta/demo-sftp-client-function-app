import paramiko
import io

def connect_to_sftp(host, username, private_key):
    # Load the private key
    private_key_bytes = private_key.encode('utf-8')
    private_key_obj = paramiko.rsakey.RSAKey.from_private_key(io.StringIO(private_key_bytes.decode('utf-8')))

    # Create an SSH client and connect to the SFTP server using the private key
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, pkey=private_key_obj)

    # Return the connected SSH client
    return ssh