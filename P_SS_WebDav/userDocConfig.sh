#!/bin/bash

#ATTENTION ! Run it to setup the necessary configurations before starting userDoc.sh and start your automatised archiving system


#This script sets up the basic configuration to launch the script
#And to use the webdav server
#python3 and webdav configuration is needed
#A crontab file is created to automate the launch of the script  
#First  install python 3 and configurate the webdav local server

echo "Installing python"
sudo apt-get install -i python3




#webdav configuration
echo "configuration WebDAV" 
apt -y install apache2-utils

mkdir /home/webdav
chown www-data. /home/webdav
chmod 770 /home/webdav
cat ./config/webdav_configuration.txt >> /etc/apache2/sites-available/webdav.conf

# Set the password directly in the script
password="testeur123"

# The username you want to set the password for
username="ubuntu"

# Specify the path to the htpasswd file
htpasswd_file="/etc/apache2/.htpasswd"

# Use the htpasswd command with the -b option to set the password
htpasswd -b -c "$htpasswd_file" "$username" "$password"

# Check for any errors
if [ $? -eq 0 ]; then
  echo "Password has been set successfully for $username"
else
  echo "Failed to set the password"
fi

a2enmod dav*
a2ensite webdav
systemctl restart apache2





