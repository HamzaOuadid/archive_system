import requests
import zipfile
import io
import tarfile
import datetime
import os
import time
import logging
from emailing import buildPayload
from emailing import sendEmail
import shutil
import hashlib
import glob
import yaml
from utilz import *
from FTP_server import *


#defining syntax for log file 
logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO, format='%(levelname)s:%(asctime)s:%(message)s')

def read_yaml(file_path):
	with open(file_path,"r") as f:
		return yaml.safe_load(f)

#Getting all variables from the yaml file
CONFIG=read_yaml("./config.yaml")


               


def getFileLink(LINK, NOTIFY):

    try:
        logging.info('Trying to connect...')
        fileLink = requests.get(LINK)
        logging.info('Connection successful')
        return fileLink
    except requests.exceptions.RequestException as e:
        logging.error(e.strerror)
        if NOTIFY:
            message = buildPayload('File retrieval', 'ERROR, review log')
            subject = 'File Retrieval Notification'
            sender_email = CONFIG['SMTP_MAIL_SENDER']
            recipient_email = CONFIG['SMTP_MAIL_RECEIVERS']
            smtp_server = CONFIG['SMTP_SERVER']
            smtp_port = CONFIG['SMTP_PORT']
            smtp_password = CONFIG['SMTP_PASSWORD']
            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)

       
def extractFile(fileLink, NOTIFY):
    path= 'test100.sql'
    target_folder = './temp'
    with zipfile.ZipFile(io.BytesIO(fileLink.content)) as archive:
        archive.extractall(target_folder)
        logging.info('EXTRACTION SUCCESSFUL: filename : test100.sql' )
    
    return path
    


def archiveFile(SQL_FILE, NOTIFY):
    path= 'temp/' + SQL_FILE
    temp = 'temp'
    last_backup = 'last_backup'
    temp_tgz = 'temp_tgz'
   
    logging.info('ARCHIVING FILE')
    if not os.path.exists(temp):
        print("Empty")
    else:
        logging.info('ARCHIVING FILE')
        now = datetime.datetime.now()
        name = now.strftime("%Y%d%m")
        logging.info("The archive name" + name)
        archiveName = './'+ name + ".tgz"
        
        
         # Create the tar.gz archive
        with tarfile.open(archiveName, 'w:gz') as archive:
            # Add the SQL file to the archive
            archive.add(temp, arcname=os.path.basename(SQL_FILE))
        


        # checking if there's a prior backup to compare with
        files = os.listdir(last_backup)

        # Filter out directories
        files = [f for f in files if os.path.isfile(os.path.join(last_backup, f))]

        # Check if there's only one file in the directory
        if len(files) == 1:
            file_name = files[0]
            compare_path = os.path.join(last_backup, file_name)
        
            # Comparing the hash of the latest backup file and the new one
            if diffrent_hashes(compare_path,archiveName , SQL_FILE)== True:
                logging.info('Hashes do not match. Proceeding with archiving.')
                add_ftp(archiveName)
                replace_tgz(compare_path, archiveName, last_backup)
                delete_file(archiveName)
                empty(temp)
                

            else:
                empty(temp)
                logging.info('Hashes match. Skipping archiving.')
        else:
            logging.info('No prior version found. Archiving directly without hash check.')
            add_ftp(archiveName)
            add_tgz(archiveName, last_backup)
            delete_file(archiveName)
            empty(temp)
            


    logging.info('ARCHIVE SUCCESSFUL')


def manageFile(Duration, durationType, NOTIFY):
    print("looking for files")
    files = os.listdir("/mnt/dav/")
    for f in files:
        if f.endswith('.tgz'):
            print(f)
            try:
                dateCreation = datetime.datetime.strptime(time.ctime(os.path.getctime("/mnt/dav/" + f)), "%c")
                now = datetime.datetime.now()
                # Compare the date of creation of the archive with the duration from configuration file
                if dateCreation + datetime.timedelta(**{durationType: Duration}) < now:
                    print("should be deleted")
                    print("-----------------")
                    try:
                        delete_ftp(f)
                        logging.info('FILES EXCEEDING DURATION DELETED')
                    except OSError as e:
                        logging.error(e.strerror)
                        if NOTIFY:
                            message = buildPayload('Files management', 'ERROR, review log')
                            subject = 'Files Management Notification'
                            sender_email = CONFIG['sender_email']
                            recipient_email = CONFIG['recipient_email']
                            smtp_server = CONFIG['smtp_server']
                            smtp_port = CONFIG['smtp_port']
                            smtp_password = CONFIG['smtp_password']
                            sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)

            except OSError:
                logging.error("Path does not exist")
                if NOTIFY:
                    message = buildPayload('File management', 'ERROR, review log')
                    subject = 'Files Management Notification'
                    sender_email = CONFIG['sender_email']
                    recipient_email = CONFIG['recipient_email']
                    smtp_server = CONFIG['smtp_server']
                    smtp_port = CONFIG['smtp_port']
                    smtp_password = CONFIG['smtp_password']
                    sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password)
                    
