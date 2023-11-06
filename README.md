# archive_system


This project's goal is to develop a robust backup system. It's designed to fetch a zip file from a web server, extract an SQL dump, verify its integrity, and then create a fresh archive in a specified format. You can customize how long this archive is retained. After that, the new archive is sent to a remote server, and you have the option of choosing between FTP or Webdav for the transfer method. This system allows for the storage of multiple versions of the backup on the destination server, and you can set a specific retention period for each version. Additionally, it generates detailed logs and email notifications to keep you informed and in control of the backup process.
