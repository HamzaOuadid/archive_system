#!/bin/bash

# Automate script execution
# Configure crontab to call our script and launch the archive of the file 
# Each day at 1 am, every day, every month, every day of the week 
# execute backup.py

# Prompt user for backup crontab username
read -p "Enter the username: " username

# Add the crontab entry with the provided values
(crontab -l ; echo "0 1 * * * /usr/bin/python3 ./backup.py") | crontab -u $username -



# Check crontab was created.
if sudo test -f "/var/spool/cron/crontabs/$username"
then
	echo "Crontab file created successfully"
	# Launch cron service
	sudo service cron start
else
	echo "Error: Cron file was not created."
fi


