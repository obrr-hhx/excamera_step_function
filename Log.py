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
    def __init__(self, bucket_name, log_file_name, start_time):
        self.bucket_name = bucket_name
        self.log_file_name = log_file_name
        self.start_time = start_time
        self.download_file_name = []
        self.start_download = []
        self.end_download = []
        self.download_file_size = []
        self.upload_file_name = []
        self.upload_file_size = []
        self.start_upload = []
        self.end_upload = []

    def log_download(self, start, end, download_file_name, download_file_size):
        self.start_download.append(start)
        self.end_download.append(end)
        self.download_file_name.append(download_file_name)
        self.download_file_size.append(download_file_size)

    def log_execute(self, start, end, command):
        self.start_execute = start
        self.end_execute = end
        self.execute_time = end-start
        self.command = command

    def log_upload(self, start, end, upload_file_name, upload_file_size):
        if type(start) != type(time.time()):
            raise TypeError("Upload time must be a floats")
        if type(end) != type(time.time()):
            raise TypeError("Upload time must be a floats")
        if type(upload_file_name) != str:
            raise TypeError("Upload file name must be a string")
        if type(upload_file_size) != int:
            raise TypeError("Upload file size must be an integer")
        self.start_upload.append(start)
        self.end_upload.append(end)
        self.upload_file_name.append(upload_file_name)
        self.upload_file_size.append(upload_file_size)
    
    # generate the log file and upload it to S3
    def log(self):
        log_content = 'id ' + self.log_file_name + '\n'
        log_content += 'start_time ' + str(self.start_time) + '\n'
        log_content += 'execute_time_start ' + str(self.start_execute) + '\n'
        log_content += 'execute_time_end ' + str(self.end_execute) + '\n'
        
        
        for i in range(len(self.download_file_name)):
            log_content += 'download_file ' + self.download_file_name[i] + ' ' + str(self.download_file_size[i]) + ' ' + str(self.start_download[i]) + ' ' + str(self.end_download[i]) + '\n'
        for i in range(len(self.upload_file_name)):
            log_content += 'upload_file ' + self.upload_file_name[i] + ' ' + str(self.upload_file_size[i]) + ' ' + str(self.start_upload[i]) + ' ' + str(self.end_upload[i]) + '\n'
        
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
        s3_client.upload_file('/tmp/'+self.log_file_name, self.bucket_name, 'log/'+self.log_file_name+'.log')
