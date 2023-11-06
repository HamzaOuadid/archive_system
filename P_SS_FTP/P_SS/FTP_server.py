import ftplib



def add_ftp(file_name):
    username = 'admin'
    password = 'fghj1234'
    server_address = 'localhost'
    port = 21
    session = ftplib.FTP()
    session.connect(server_address, port)
    session.login(user=username, passwd=password)
    with open(file_name, 'rb') as file:   
        session.storbinary('STOR {}'.format(file.name), file)
    session.quit()

def retrieve_ftp( file_name):
    username = 'admin'
    password = 'afghj1234'
    server_address = 'localhost'
    port = 21
    session = ftplib.FTP()
    session.connect(server_address, port)
    session.login(user=username, passwd=password)
    retrieved_file_name = '_' + file_name
    with open(retrieved_file_name, 'wb') as retrieved_file:
        session.retrbinary('RETR ' + file_name, retrieved_file.write)
    session.quit()
    return retrieved_file

def delete_ftp(file_name):
    username = 'admin'
    password = 'fghj1234'
    server_address = 'localhost'
    port = 21
    session = ftplib.FTP()
    session.connect(server_address, port)
    session.login(user=username, passwd=password)
    session.delete(file_name)
    session.quit()