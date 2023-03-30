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
    start_download_time = get_time()
    s3_client.download_file(bucket_name, video_key, local_file_path)
    end_download_time = get_time()
    # current_time = get_time()
    # download_time = current_time - base_time
    # base_time = current_time

    # execute the vpxenc command
    output_file_name = ''
    if video_key == '00000000-vpxenc.ivf':
        output_file_name = '00000000.ivf'
    else:
        output_file_name = video_key.split('-')[0] + '-0.ivf'
    output_file_path = '/tmp/' + output_file_name
    command = ['./xc-terminate-chunk', local_file_path, output_file_path]
    start_execute_time = get_time()
    subprocess.run(command)
    end_execute_time = get_time()
    # current_time = get_time()
    # xc_terminate_chunk_time = current_time - base_time
    # base_time = current_time

    # upload the output file to S3
    start_upload_time = get_time()
    s3_client.upload_file(output_file_path, bucket_name, output_file_name)
    end_upload_time = get_time()
    # current_time = get_time()
    # upload_time = current_time - base_time
    # base_time = current_time

    # generate the log file and upload it to S3
    log = Log(bucket_name, command[0].replace('./', '')+video_key, start_time=start_time)
    log.log_download(start_download_time, end_download_time, download_file_name=video_key, download_file_size=os.path.getsize(local_file_path))
    log.log_execute(start_execute_time, end_execute_time, command)
    log.log_upload(start_upload_time, end_upload_time, upload_file_name=output_file_name, upload_file_size=os.path.getsize(output_file_path))
    log.log()

    # return the output file name
    return {'xc-terminate-chunk': output_file_name}