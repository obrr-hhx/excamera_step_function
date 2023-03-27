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
    video_key = event['vpxenc']
    bucket_name = event['bucket']

    # get the video from S3
    local_file_path = '/tmp/' + video_key
    s3_client.download_file(bucket_name, video_key, local_file_path)
    current_time = get_time()
    download_time = current_time - base_time
    base_time = current_time

    # execute the vpxenc command
    output_file_name = ''
    if video_key == '00000000-vpxenc.ivf':
        output_file_name = '00000000.ivf'
    else:
        output_file_name = video_key.split('-')[0] + '-0.ivf'
    output_file_path = '/tmp/' + output_file_name
    command = ['./xc-terminate-chunk', local_file_path, output_file_path]
    subprocess.run(command)
    current_time = get_time()
    xc_terminate_chunk_time = current_time - base_time
    base_time = current_time

    # upload the output file to S3
    s3_client.upload_file(output_file_path, bucket_name, output_file_name)
    current_time = get_time()
    upload_time = current_time - base_time
    base_time = current_time

    # generate the log file and upload it to S3
    log = Log(bucket_name, command[0].replace('./', '')+video_key)
    log.log_download(download_time, download_file_name=video_key, download_file_size=os.path.getsize(local_file_path))
    log.log_execute(xc_terminate_chunk_time, command)
    log.log_upload(upload_time, upload_file_name=output_file_name, upload_file_size=os.path.getsize(output_file_path))
    log.log()

    # return the output file name
    return {'xc-terminate-chunk': output_file_name}