'''
0000003.ivf: 00000003.y4m 00000003-1.ivf 00000002-0.state 00000002-1.state
	xc-enc -W -w 0.75 -i y4m -o 00000003.ivf -r -I 00000002-1.state -p 00000003-1.ivf -S 00000002-0.state  00000003.y4m
'''

import subprocess
import boto3
import time
import os

from Log import Log

s3_client = boto3.client('s3')

def get_time():
    return time.time() * 1000

def compute_time(base_time):
    current_time = get_time()
    time = current_time - base_time
    base_time = current_time
    return time

def lambda_handler(event, context):
    start_time = get_time()
    base_time = start_time

    # get the video name from the event
    download_key = [event['video'], event['xc-enc-00000003'], event['xc-dump'], event['xc-enc-rebase']]
    
    bucket_name = event['bucket']

    # get the video from S3
    download_time = []
    for key in download_key:
        s3_client.download_file(bucket_name, key, '/tmp/'+key)
        download_time.append(compute_time(base_time))

    # execute the xc-enc command to get the .ivf file
    output_ivf = download_key[0].split('.')[0] + '.ivf'

    command = ['./xc-enc', '-W', '-w', '0.75', '-i', 'y4m', '-o', '/tmp/'+output_ivf, '-r', '-I', '/tmp/'+download_key[3], '-p', '/tmp/'+download_key[1], '-S', '/tmp/'+download_key[2], '/tmp/'+download_key[0]]
    subprocess.run(command)
    xc_enc_time = compute_time(base_time)

    # upload the output file to S3
    s3_client.upload_file('/tmp/'+output_ivf, bucket_name, output_ivf)
    upload_time = compute_time(base_time)

    # generate the log file and upload it to S3
    log = Log(bucket_name=bucket_name, log_file_name='rebase_'+command[0].replace('./', '')+download_key[0])
    for i in range(len(download_time)):
        log.log_download(download_time[i], download_file_name=download_key[i], download_file_size=os.path.getsize('/tmp/'+download_key[i]))
    log.log_execute(xc_enc_time, command)
    log.log_upload(upload_time, output_ivf, upload_file_size=os.path.getsize('/tmp/'+output_ivf))
    log.log()
    
    # return the output file name
    return {
        'xc-enc-ivf': output_ivf
    }