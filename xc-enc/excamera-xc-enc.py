#00000001-1.state 00000001.ivf: 00000001.y4m 00000001-0.ivf 00000000-0.state
#	xc-enc -W -w 0.75 -i y4m -o 00000001.ivf -r -I 00000000-0.state -p 00000001-0.ivf -O 00000001-1.state 00000001.y4m

import subprocess
import boto3
import os
import time

from Log import Log

s3_client = boto3.client('s3')

def get_time():
    return time.time() * 1000

def lambda_handler(event, context):
    start_time = get_time()
    base_time = start_time

    # get the video name from the event
    download_key = [event['video'], event['xc-terminate-chunk'], event['xc-dump']]
    
    bucket_name = event['bucket']

    # get the video from S3
    download_time = []
    for key in download_key:
        s3_client.download_file(bucket_name, str(key), '/tmp/'+str(key))
        current_time = get_time()
        download_time.append(current_time - base_time)
        base_time = current_time

    # execute the xc-enc command to get the .state file and .ivf file
    output_state = download_key[0].split('.')[0] + '-1.state'
    output_ivf = download_key[0].split('.')[0] + '.ivf'

    command = ['./xc-enc', '-W', '-w', '0.75', '-i', 'y4m', '-o', '/tmp/'+output_ivf, '-r', '-I', '/tmp/'+download_key[2], '-p', '/tmp/'+download_key[1] ,'-O', '/tmp/'+output_state, '/tmp/'+download_key[0]]
    subprocess.run(command)
    current_time = get_time()
    xc_enc_time = current_time - base_time
    base_time = current_time

    # check if the output state file is existing in the /tmp folder
    # if not, then the xc-enc command failed
    if not os.path.exists('/tmp/'+output_state):
        raise Exception('xc-enc failed to generate the state file')

    # upload the output file to S3
    s3_client.upload_file('/tmp/'+output_ivf, bucket_name, output_ivf)
    current_time = get_time()
    upload_ivf_time = current_time - base_time
    base_time = current_time

    s3_client.upload_file('/tmp/'+output_state, bucket_name, output_state)
    current_time = get_time()
    upload_state_time = current_time - base_time
    base_time = current_time

    # generate the log file and upload it to S3
    log = Log(bucket_name=bucket_name, log_file_name=command[0].replace('./', '')+download_key[0])
    for i in len(download_key):
        log.lod_download(download_time[i], download_key[i], download_file_size=os.path.getsize('/tmp/'+download_key[i]))
    log.log_execute(xc_enc_time, command)
    log.log_upload(upload_ivf_time, output_ivf, upload_file_size=os.path.getsize('/tmp/'+output_ivf))
    log.log_upload(upload_state_time, output_state, upload_file_size=os.path.getsize('/tmp/'+output_state))
    log.log()

    # return the output file name
    return {
        'xc-enc-ivf': output_ivf,
        'xc-enc-state': output_state
    }