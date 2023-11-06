from backupUtilities import *
import json

# Load the configuration from the JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

# Define the list of required configuration keys
required_keys = ["url_zip", "absolute_path", "sql_file_name", "url_webdav", "nom_utilisateur", "mot_de_passe", "retention_period", "recipients", "SMTP_PORT", "SMTP_SERVER", "SMTP_PASSWORD", "SMTP_MAIL_SENDER"]
# Check if all required configuration keys are present
if all(key in config for key in required_keys):
    # All required configuration values are present
    url_zip = config["url_zip"]
    absolute_path = config["absolute_path"]
    sql_file_name = config["sql_file_name"]
    url_webdav = config["url_webdav"]
    nom_utilisateur = config["nom_utilisateur"]
    mot_de_passe = config["mot_de_passe"]
    retention_period = config["retention_period"]
    recipients = config.get("recipients", [])
    smtp_port = config["SMTP_PORT"]
    smtp_server = config["SMTP_SERVER"]
    smtp_password = config["SMTP_PASSWORD"]
    mail_sender = config["SMTP_MAIL_SENDER"]
    logging.info("Configuration values were imported correctly.")
else:
    # Some required configuration values are missing
    missing_keys = [key for key in required_keys if key not in config]
    logging.error(f"Some required configuration values are missing or incorrect in the 'config.json' file: {', '.join(missing_keys)}. Please check the configuration.")

# Paths of download and extraction based on the chosen absolute path
destination_zip_download = Path(rf'{absolute_path}/sql.zip')
destination_zip_extract = Path(rf'{absolute_path}/extractedSQLFolder')
repertoire_archived = Path(rf'{absolute_path}')

# Configuration of the file format name .tgz as DD-MM-YYYY
date_actuelle = datetime.datetime.now()
nom_archive = date_actuelle.strftime("%Y%d%m") + ".tgz"
archive_tgz = f"{repertoire_archived}/{nom_archive}"

logging.info(f"----STARTING THE SCRIPT-----")

# Summary will stock the steps done during the script and will be sent by mail
summary = '''Hello there,
You are receiving this email to keep up to date with what is happening with your archiving management system.
You find attached the log file to track the execution of your scripts.\n
'''
subject = f"Archiving Script of {datetime.datetime.now().strftime('%d-%m-%Y')}"

# Start by cleaning old archives
logging.info("Cleaning old archives:")
clean_old_archives(url_webdav, nom_utilisateur, mot_de_passe, retention_period)
logging.info(f"Old archives exceeding {retention_period} days have been checked and deleted successfully. The process begins.")
summary += f"---Old archives exceeding {retention_period} days have been checked and deleted successfully.\n"

# Extracting the last file from the archive system
logging.info("Extracting the latest archive:")
directory_last_archived, last_archived_name = extract_latest_archive(url_webdav, nom_utilisateur, mot_de_passe, repertoire_archived)


# Downloading the zip file from web server
if telecharger_zip(url_zip, destination_zip_download):
    summary += f"---The file {sql_file_name} has been successfully downloaded from the WEB server.\n"
    # Extracting the content of the zip file (sql file) to /temp
    if extraire_zip(destination_zip_download, destination_zip_extract):
        # Check here if directory_last_archived and last_archived_name return None
        if directory_last_archived is None:
            summary += f"---The WebDAV server did not contain any archive; inserting the first archive {nom_archive}.\n"
            # Creating and archiving the .tgz
            if creer_archive_tgz(destination_zip_extract, archive_tgz):
                logging.info("The .tgz archive has been created successfully. The process continues.")
                summary += f"---The {nom_archive} archive has been created successfully.\n"
                transfer_archive_to_webdav(url_webdav, nom_utilisateur, mot_de_passe, archive_tgz, nom_archive)
                summary += f"---The {nom_archive} archive has been successfully transferred to the WebDAV server.\n"
	    # Error in creating the .tgz	
            else:
                logging.error("Failed to create the .tgz archive.")
                summary += f"---There was an error during the creation of {nom_archive}.\n"
        # Case where there's an archived file on our remote WebDAV Server
        else:
            sqlfile_webserver = f"{destination_zip_extract}/{sql_file_name}"
            last_archived_webdav = f"{directory_last_archived}/{sql_file_name}"
            logging.info(f"Comparing files: {sqlfile_webserver} and {last_archived_webdav}")
	    # Check if sqlfile imported from webserver has been modified
            if check_compatibility(sqlfile_webserver, last_archived_webdav):
                logging.info("Both files are compatible. No archiving is performed.")
                summary += f"---Comparison of {sql_file_name} from the last archive and {sql_file_name} extracted from the WEB server: both files are compatible, and no archiving is performed.\n"
	    # Both files are not the same, starting archiving process 
            else:
                logging.info("Both files are not compatible. Archiving begins.")
                summary += f"---Comparison of {sql_file_name} from the last archive and {sql_file_name} extracted from the WEB server: {sql_file_name} has been modified, and archiving begins.\n"
                # Creating and archiving the .tgz
                if creer_archive_tgz(destination_zip_extract, archive_tgz):
                    logging.info("The .tgz archive has been created successfully. The process continues.")
                    summary += f"---The {nom_archive} archive has been created successfully.\n"
                    transfer_archive_to_webdav(url_webdav, nom_utilisateur, mot_de_passe, archive_tgz, nom_archive)
                    summary += f"---The {nom_archive} archive has been successfully transferred to the WebDAV server.\n"
                # Error in creating the .tgz
                else:
                    logging.error("Failed to create the .tgz archive.")
                    summary += f"---There was an error during the creation of {nom_archive}.\n"
    # Failed in extracting the content of the zip file (sql file) to /temp
    else:
        logging.error(f"Failed to extract {sql_file_name} after downloading.")
        summary += f"---There was a problem during the extraction of {sql_file_name} after downloading.\n"
# Downloading the zip file from web server
else:
    logging.error(f"Failed to download {sql_file_name}.")
    summary += f"---There was a problem during the download of {sql_file_name}.\n"

logging.info(f"----ENDING THE SCRIPT-----")

summary += f"\n\nENSIAS TEAM"

if sendEmail(summary, subject, recipients, mail_sender, smtp_server, smtp_port, smtp_password):
    pass
