# Log class
# Author: Handson Huang

# the Log class is used to log the information of the excamera step function
# the log file is stored in the S3 bucket

# the log class has the following attributes:
# 1. bucket_name: the name of the S3 bucket
# 2. log_file_name: the name of the log file
# 3. download_time: the time used to download the file from S3
# 4. execute_time: the time used to execute the command
# 5. upload_time: the time used to upload the file to S3
# 6. download_file_name: the name of the file downloaded from S3
# 7. dowmload_file_size: the size of the file downloaded from S3
# 8. upload_file_name: the name of the file uploaded to S3
# 9. upload_file_size: the size of the file uploaded to S3
# 10. command: the command executed
# 11. id: the id of the log file

import boto3
import time

class Log:
    # log initialization
    def __init__(self, bucket_name, log_file_name):
        self.bucket_name = bucket_name
        self.log_file_name = log_file_name
        self.download_file_name = []
        self.download_file_size = []
        self.upload_file_name = []
        self.upload_file_size = []

    def log_download(self, download_time, download_file_name, download_file_size):
        self.download_time = download_time
        self.download_file_name.append(download_file_name)
        self.download_file_size.append(download_file_size)

    def log_execute(self, execute_time, command):
        self.execute_time = execute_time
        self.command = command

    def log_upload(self, upload_time, upload_file_name, upload_file_size):
        if type(upload_time) != type(time.time()):
            raise TypeError("Upload time must be a floats")
        if type(upload_file_name) != str:
            raise TypeError("Upload file name must be a string")
        if type(upload_file_size) != int:
            raise TypeError("Upload file size must be an integer")
        self.upload_time = upload_time
        self.upload_file_name = upload_file_name
        self.upload_file_size = upload_file_size
    
    # generate the log file and upload it to S3
    def log(self):
        log_content = 'id ' + self.log_file_name + '\n'
        log_content += 'download_time ' + str(self.download_time) + '\n'
        log_content += 'execute_time ' + str(self.execute_time) + '\n'
        log_content += 'upload_time ' + str(self.upload_time) + '\n'
        
        for i in range(len(self.download_file_name)):
            log_content += 'download_file_name ' + self.download_file_name[i] + ' ' + str(self.download_file_size[i]) + '\n'
        for i in range(len(self.upload_file_name)):
            log_content += 'upload_file_name ' + self.upload_file_name[i] + ' ' + str(self.upload_file_size[i]) + '\n'
        
        log_content += 'command '
        for i in range(len(self.command)):
            if i == len(self.command) - 1:
                log_content += self.command[i] + '\n'
            else:    
                log_content += self.command[i] + ' '

        # write the log file
        with open('/tmp/'+self.log_file_name, 'w') as f:
            f.write(log_content)

        # upload the log file to S3 directory which is named 'log/'
        s3_client = boto3.client('s3')
        s3_client.upload_file('/tmp/'+self.log_file_name, self.bucket_name, 'log/'+self.log_file_name)
