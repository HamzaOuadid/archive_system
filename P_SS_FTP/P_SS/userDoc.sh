#!/bin/bash
#This script sets up the basic configuration to launch the script
#And to use the FTP server
#python3 and docker are needed 
#A crontab file is created to automate the launch of the script  
#First  install python 3 and devafs2

echo "Installing python"
sudo apt-get install -i python3
echo "Installing docker"
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
#checking if docker version
docker --version 
#runing the FTP server container
docker compose up 

# Automate script execution
# Configure crontab to call projet.py and launch the archive of the file 
# Each day at 1 am, every day, every month, every day of the week 
# execute projet.py

# Prompt user for backup directory and username
read -p "Enter the backup directory path: " backup_dir
read -p "Enter the username: " username

# Add the crontab entry with the provided values
(crontab -l ; echo "0 1 * * * /usr/bin/python3 $backup_dir/backup.py") | crontab -u $username -

# Check crontab was created.
if sudo test -f "/var/spool/cron/crontabs/$username"
then
	echo "Crontab file created successfully"
	# Launch cron service
	sudo service cron start
else
	echo "Error: Cron file was not created."
fi


