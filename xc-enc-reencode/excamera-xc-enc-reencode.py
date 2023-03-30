'''
00000002-1.ivf: 00000002.y4m 00000002-0.ivf 00000001-0.state
	xc-enc -W -w 0.75 -i y4m -o 00000002-1.ivf -r -I 00000001-0.state -p 00000002-0.ivf  00000002.y4m
'''
import json
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
    star_time = get_time()
    base_time = star_time

    # get the video name from the event
    download_key = []
    download_key.append(event['video'])
    download_key.append(event['xc-terminate-chunk']) 
    download_key.append(event['xc-dump'])
    
    bucket_name = event['bucket']

    start_download_time = []
    end_download_time = []
    # get the video from S3
    for key in download_key:
        start_download_time.append(get_time())
        s3_client.download_file(bucket_name, key, '/tmp/'+key)
        end_download_time.append(get_time())
        # current_time = get_time()
        # download_time.append(current_time - base_time)
        # base_time = current_time
        # download_time.append(compute_time(base_time))

    # execute the xc-enc command to get the .ivf file
    output_ivf = download_key[0].split('.')[0] + '-1.ivf'

    command = ['./xc-enc', '-W', '-w', '0.75', '-i', 'y4m', '-o', '/tmp/'+output_ivf, '-r', '-I', '/tmp/'+download_key[2], '-p', '/tmp/'+download_key[1], '/tmp/'+download_key[0]]
    start_execute_time = get_time()
    subprocess.run(command)
    end_execute_time = get_time()
    # current_time = get_time()
    # xc_enc_time = current_time - base_time
    # base_time = current_time
    # xc_enc_time = compute_time(base_time)


    # upload the output file to S3
    start_upload_time = get_time()
    s3_client.upload_file('/tmp/'+output_ivf, bucket_name, output_ivf)
    end_upload_time = get_time()
    # current_time = get_time()
    # upload_time = current_time - base_time
    # base_time = current_time
    # upload_time = compute_time(base_time)
    
    # generate the log file and upload it to S3
    log = Log(bucket_name=bucket_name, log_file_name='reencode_'+command[0].replace('./', '')+download_key[0], start_time=star_time)
    for i in range(len(download_key)):
        log.log_download(start_download_time[i], end_download_time[i], download_key[i], download_file_size=os.path.getsize('/tmp/'+download_key[i]))
    log.log_execute(start_execute_time, end_execute_time, command)
    log.log_upload(start_upload_time, end_upload_time, output_ivf, upload_file_size=os.path.getsize('/tmp/'+output_ivf))
    log.log()

    # return the output file name
    return {
        'xc-enc-ivf': output_ivf
    }