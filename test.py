#!/usr/bin/env python3

# write_time = 1679997294824.7717+456.259033203125+3029.782958984375+3098.5380859375
# read_time = 1679997299136.9507+458.524658203125

# time = read_time-write_time

# print("write time ",write_time)
# print("read time ",read_time)
# print("time ",time)

# read the content of ./log/log_2/reencode_xc-enc00000002.y4m.log
# and parse the content to get the time
path1 = './log/log_2/reencode_xc-enc00000002.y4m.log'
reencode_log = {'start_time': 0, 'download_time': 0, 'execute_time': 0, 'upload_time': 0}

path2 = './log/log_2/rebase_xc-enc00000002.y4m.log'
rebase_log = {'start_time': 0, 'download_time': 0, 'execute_time': 0, 'upload_time': 0}

def parse_time(path, log_dict):
    with open(path, 'r') as log:
        for line in log:
            if line.startswith('start_time'):
                log_dict['start_time'] = float(line.split()[1])
            elif line.startswith('download_time'):
                log_dict['download_time'] = float(line.split()[1])
            elif line.startswith('execute_time'):
                log_dict['execute_time'] = float(line.split()[1])
            elif line.startswith('upload_time'):
                log_dict['upload_time'] = float(line.split()[1])

# parse_time(path1, reencode_log)
# parse_time(path2, rebase_log)

# write_time = reencode_log['start_time']+reencode_log['download_time']+reencode_log['execute_time']+reencode_log['upload_time']
# read_time = rebase_log['start_time']+rebase_log['download_time']

# time = read_time-write_time

# print("write time ",write_time)
# print("read time ",read_time)
# print("time ",time)

write_time = 1680080609797.3518
read_time = 1680080610828.5474
time = read_time-write_time

print("write time "+'\t',write_time)
print("read time "+'\t',read_time)
print("time "+'\t',time)