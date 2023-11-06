import os
import requests
import zipfile
import shutil
import tarfile
import datetime
import hashlib
import logging
import logging.handlers
import smtplib
import ssl
import xml.etree.ElementTree as ET
from datetime import timedelta
from pathlib import Path
from webdav3.client import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


log_file = 'backup_exe.log'

# Initialize logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Add %(asctime)s to include the timestamp
    datefmt='%Y-%m-%d %H:%M:%S',  # Define the format for the timestamp
    filemode='w'			#Will overwrite the logs in each script (to send them on mail)
)

'''
# Create a custom handler to add a separator line
class SeparatorHandler(logging.handlers.RotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        with open(self.baseFilename, 'a') as file:
            file.write('-' * 10)  # Add a separator line

# Add the custom handler to the root logger (if I want logs to get stacked in backup_exe.log, set maxBytes to 0)
logging.root.addHandler(SeparatorHandler('backup_exe.log', maxBytes=1, backupCount=0))
'''


'''BACKUP FUNCTIONS DEFINITION STARTS NOW'''


# Download a zip file from an URL to a local_path
def telecharger_zip(url, local_path):
    try:
        response = requests.get(url, stream=True, verify=False)  # Disabling SSL verification
        if response.status_code == 200:
            with open(local_path, 'wb') as local_file:
                for chunk in response.iter_content(chunk_size=128):
                    local_file.write(chunk)
            logging.info(f"The .zip file was successfully downloaded from {url} and saved to {local_path}")
            return True
        else:
            logging.error(f"Failed to download the .zip file from {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"An error occurred during download: {str(e)}")
        return False




# Extract a .zip file
def extraire_zip(zip_path, destination_directory):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_directory)
        logging.info(f"The .zip file has been successfully extracted to {destination_directory}")
        return True
    except Exception as e:
        logging.error(f"An error occurred while extracting the .zip file: {str(e)}")
        return False

# Compare if two files are identical
def check_compatibility(file1, file2):
    with open(file1, 'rb') as f:
        hash1 = hashlib.md5(f.read()).hexdigest()

    with open(file2, 'rb') as f:
        hash2 = hashlib.md5(f.read()).hexdigest()

    return hash1 == hash2


    
# Creating an archive from a path
def creer_archive_tgz(repertoire, archive_tgz):
    try:
        with tarfile.open(archive_tgz, "w:gz") as tar:
            for root, _, files in os.walk(repertoire):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, repertoire)
                    tar.add(file_path, arcname=arcname)
            # Add a log message to indicate that the archive has been successfully created
            logging.info(f"The .tgz archive has been created successfully: {archive_tgz}")
            return True
    except Exception as e:
        # Add a log message in case of an error
        logging.error(f"An error occurred while creating the .tgz archive: {str(e)}")
        return False




# Check the status of the WebDAV connection
def check_webdav_connection(url_webdav, username, password):
    try:
        response = requests.head(url_webdav, auth=(username, password))
        if response.status_code == 200:
            # Add a log message to indicate a successful connection
            logging.info("Connected to the WebDAV server successfully.")
            return True
        else:
            # Add a log message in case of a connection failure
            logging.error(f"Failed to connect to the WebDAV server. Status code: {response.status_code}")
    except Exception as e:
        # Add a log message in case of an error
        logging.error(f"An error occurred during the connection: {str(e)}")
    return False



# Transfer the generated .tgz archive to our local WebDAV server
def transfer_archive_to_webdav(url_webdav, username, password, archive_tgz, file_name):
    try:
        if check_webdav_connection(url_webdav, username, password):
            url_destination = f"{url_webdav}/{file_name}"
            
            # Ensure that the archive file is accessible
            if os.path.exists(archive_tgz):
                with open(archive_tgz, 'rb') as fichier:
                    response = requests.put(url_destination, data=fichier, auth=(username, password))
                if response.status_code == 201 or response.status_code == 204:
                    logging.info(f"The .tgz archive has been successfully transferred to {url_destination}")
                else:
                    logging.error(f"Failed to transfer the .tgz archive. Status code: {response.status_code}")
            else:
                logging.error(f"Archive file '{archive_tgz}' does not exist or is inaccessible. Check local permissions.")
    except Exception as e:
        logging.error(f"An error occurred during the transfer: {str(e)}")



# Clean archives that have exceeded the "retention_period" days
def clean_old_archives(url_webdav, username, password, retention_period):
    try:
        # Calculate the current date
        current_date = datetime.datetime.now()

        # Access the root of the WebDAV server
        url_path = url_webdav
        response = requests.request("PROPFIND", url_path, auth=(username, password))

        if response.status_code == 207:
            # Parse the XML response
            root = ET.fromstring(response.text)

            # Iterate through the 'response' elements
            for response_elem in root.findall('.//{DAV:}response'):
                href_elem = response_elem.find('{DAV:}href')
                if href_elem is not None:
                    file_name = href_elem.text.strip('/')  # Extract file name from the 'href' element

                    # Try to parse the date from the file name
                    try:
                        year = int(file_name[:4])
                        month = int(file_name[4:6])
                        day = int(file_name[6:8])
                        last_modified = datetime.datetime(year, day, month)
                        age = current_date - last_modified

                        if age > timedelta(days=retention_period):
                            # If the file is older than the retention period, delete it
                            url_file = f"{url_path}/{file_name}"
                            response = requests.delete(url_file, auth=(username, password))
                            if response.status_code == 204:
                                logging.info(f"Archived file '{file_name}' deleted as it exceeds the retention period.")
                            else:
                                logging.error(f"Failed to delete archived file '{file_name}' with status code: {response.status_code}")
                    except ValueError:
                        logging.warning(f"Skipping file '{file_name}' - invalid date format")

                else:
                    logging.error(f"Failed to list files in the remote path. Status code: {response.status_code}")

        else:
            logging.error(f"Failed to list files in the remote path. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f"An error occurred while cleaning old archives: {str(e)}")



#Extract Latest Archive from a WebDAV Server
def extract_latest_archive(url_webdav, username, password, destination_directory):
    try:
        options = {
            'webdav_hostname': url_webdav,
            'webdav_login': username,
            'webdav_password': password
        }
        client = Client(options)

        # List files in the WebDAV directory
        file_list = client.list()

        # Filter the list to keep only .tgz files
        tgz_files = [f for f in file_list if f.endswith('.tgz')]

        if not tgz_files:
            logging.warning("No .tgz files found on the WebDAV server.")
            return None, None

        # Find the latest .tgz file based on the file names (assuming they follow a YYYYMMDD.tgz naming convention)
        latest_tgz = max(tgz_files)
        logging.info(f"Latest file '{latest_tgz}' found on the WebDAV server.")

        # Define the local file path for the downloaded archive
        local_archive_path = f"{destination_directory}/{latest_tgz}"

        # Download the latest archive
        client.download_sync(latest_tgz, local_archive_path)

        logging.info(f"Latest file '{latest_tgz}' downloaded successfully to {local_archive_path}")

        # Define the local directory path for extraction
        extraction_directory = f"{destination_directory}/extracted_last_archive"

        # Extract the archive to the local directory
        with tarfile.open(local_archive_path, "r:gz") as tar:
            tar.extractall(path=extraction_directory)

        logging.info(f"Archive extracted to the local directory '{extraction_directory}'")

        # Return the path of the extraction directory and the name of the latest .tgz file
        return extraction_directory, latest_tgz

    except Exception as e:
        logging.error(f"An error occurred during the archive extraction: {str(e)}")
        return None, None

        


#Send log file and a message resuming the state of our running script
def sendEmail(message, subject, recipients, sender_email, smtp_server, smtp_port, smtp_password):
    for to_email in recipients:
        try:
            # Create a MIMEText object to represent the email content
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach the message as plain text + add log file
            msg.attach(MIMEText(message, 'plain'))
            
            filename = "backup_exe.log"
            attachment = open(filename, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(part)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender_email, smtp_password)
                logging.info("Logged in to your email successfully.")
                server.sendmail(sender_email, to_email, msg.as_string())
                server.quit()
                logging.info(f"Email sent to {to_email} successfully.")
        except Exception as e:
            logging.error(f"Error sending email to {to_email}: {str(e)}")
