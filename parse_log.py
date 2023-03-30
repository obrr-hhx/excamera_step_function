#!/usr/bin/env python3

import os
import sys
import csv
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

datadir = sys.argv[1]

app_start_time = 0
app_end_time = 0

data_points = []
headers = []
myLog = []
lambda_list = []
interdata_list = []

class InterData:
    def __init__(self) -> None:
        self.name = ''
        self.start_write_time = []
        self.end_write_time = []
        self.start_read_time = []
        self.end_read_time = []
        self.lifetime = 0
        self.size = 0
        self.read_lambda = [] # record which lambda read this intermediate data
        self.write_lambda = [] # record which lambda write this intermediate data

    def compute_lifetime(self):
        global app_start_time
        global app_end_time
        if len(self.start_write_time) == 0:
            self.lifetime = max(self.end_read_time) - app_start_time
        elif len(self.start_read_time) != 0 and len(self.start_write_time) != 0:
            self.lifetime = max(self.end_read_time) - min(self.end_write_time)
        else:
            self.lifetime = app_end_time - min(self.end_write_time)

class Lambda:
    def __init__(self) -> None:
        self.name = ''
        self.download_time = 0
        self.execute_time = 0
        self.upload_time = 0

        self.execute_command = ''

        # download data
        self.download_data = []
        self.download_size = []
        self.download_start_time = []
        self.download_end_time = []
        # upload data
        self.upload_data = []
        self.upload_size = []
        self.upload_start_time = []
        self.upload_end_time = []
        
        self.parent_lambda = []
        self.child_lambda = []


def create_lambda(logfile):
    global lambda_list
    lam = Lambda()
    for log in logfile:
        if log[0] == 'name':
            lam.name = log[1]
        elif log[0] == 'start_time':
            lam.start_time = float(log[1]) 
        elif log[0] == 'execute_time':
            lam.execute_time = float(log[1])
        elif log[0] == 'download_file':
            lam.download_data.append(log[1])
            lam.download_size.append(int(log[2]))
            lam.download_start_time.append(float(log[3]))
            lam.download_end_time.append(float(log[4]))
        elif log[0] == 'upload_file':
            lam.upload_data.append(log[1])
            lam.upload_size.append(int(log[2]))
            lam.upload_start_time.append(float(log[3]))
            lam.upload_end_time.append(float(log[4]))
        elif log[0] == 'command':
            lam.execute_command = log[1]
    lambda_list.append(lam)

def create_interdata():
    global lambda_list
    global interdata_list

    for lam in lambda_list:
        # check the data that is read by this lambda
        for data in lam.download_data:
            found = False
            # check if this data is already in the list
            # if yes, append which time the data is read and lambda name that read this data
            for interdata in interdata_list:
                if interdata.name == data:
                    # interdata.read_time.append(lam.start_time+lam.download_time)
                    interdata.start_read_time.append(lam.download_start_time[lam.download_data.index(data)])
                    interdata.end_read_time.append(lam.download_end_time[lam.download_data.index(data)])
                    interdata.read_lambda.append(lam.name)
                    found = True
                    break
            # if not, create a new interdata and append it to the list
            if not found:
                interdata = InterData()
                interdata.name = data
                interdata.start_read_time.append(lam.download_start_time[lam.download_data.index(data)])
                interdata.end_read_time.append(lam.download_end_time[lam.download_data.index(data)])
                interdata.read_lambda.append(lam.name)
                interdata.size = lam.download_size[lam.download_data.index(data)]
                interdata_list.append(interdata)

        # check the data that is written by this lambda
        for data in lam.upload_data:
            found = False
            # check if this data is already in the list
            # if yes, append which time the data is written and lambda name that write this data
            for interdata in interdata_list:
                if interdata.name == data:
                    # interdata.write_time.append(lam.start_time+lam.download_time+lam.execute_time+lam.upload_time)
                    interdata.start_write_time.append(lam.upload_start_time[lam.upload_data.index(data)])
                    interdata.end_write_time.append(lam.upload_end_time[lam.upload_data.index(data)])
                    interdata.write_lambda.append(lam.name)
                    found = True
                    break
            # if not, create a new interdata and append it to the list
            if not found:
                interdata = InterData()
                interdata.name = data
                # interdata.write_time.append(lam.start_time)
                interdata.start_write_time.append(lam.upload_start_time[lam.upload_data.index(data)])
                interdata.end_write_time.append(lam.upload_end_time[lam.upload_data.index(data)])
                interdata.write_lambda.append(lam.name)
                interdata.size = lam.upload_size[lam.upload_data.index(data)]
                interdata_list.append(interdata)
'''
    Parse the log file in given path
'''
def parse_log(path):
    global myLog
    for logfile in os.listdir(path):
        file_path = os.path.join(path, logfile)
        with open(file_path, 'r') as log:
            log_file = []
            read_num = 0
            write_num = 0
            for line in log:
                # record the name of log file
                
                if not log_file:
                    log_file.append(('name', logfile))
                else:
                    log_file.append(tuple(line.split()))
                if line.startswith('download_file'):
                    read_num += 1
                elif line.startswith('upload_file'):
                    write_num += 1
            log_file.append(('read_num', read_num))
            log_file.append(('write_num', write_num))

            create_lambda(log_file)
            myLog.append(log_file)

'''
    Create the CDF of the intermediate data
'''
def plot_cdf(datalog):
    path = os.path.abspath('.') + '/temp/cdf/'
    if not os.path.exists(path):
        os.mkdir(path)
    
    for (name, data) in datalog.items():
        denominator = len(data)
        Data = pd.Series(data)
        Fre=Data.value_counts()
        Fre_sort=Fre.sort_index(axis=0,ascending=True)
        Fre_df=Fre_sort.reset_index()
        Fre_df[0]=Fre_df[0]/denominator
        Fre_df.columns=[name,'Fre']
        Fre_df['cumsum']=np.cumsum(Fre_df['Fre'])
        Fre_df.to_excel(path+name+'.xlsx')
        # print(Fre_df)

        #创建画布
        plot=plt.figure()
        #只有一张图，也可以多张
        ax1=plot.add_subplot(1,1,1)
        #按照Rds列为横坐标，累计概率分布为纵坐标作图
        ax1.plot(Fre_df[name],Fre_df['cumsum'])
        #图的标题
        ax1.set_title("CDF of " + name)
        #横轴名
        if name == 'read_size' or name == 'write_size' or name == 'interdata_size':
            ax1.set_xlabel(name+' (bytes)')
        elif name == 'lifetime':
            ax1.set_xlabel('lifetime (ms)')
        else:
            ax1.set_xlabel(name)
        #纵轴名
        ax1.set_ylabel("P")
        #横轴的界限
        ax1.set_xlim(min(data),max(data))
        path_fig = path+name
        plt.savefig(path_fig)

def create_cdf(logfile):
    global interdata_list
    data_log = {'read_num': [], 'write_num': [], 'read_size': [], 'write_size': [],'lifetime': [], 'interdata_size': []}
    for log in logfile:
        read_size = 0
        write_size = 0
        for t in log:
            if t[0] == 'read_num':
                data_log['read_num'].append(int(t[1]))
            elif t[0] == 'write_num':
                data_log['write_num'].append(int(t[1]))
            elif t[0] == 'download_file':
                read_size += int(t[2])
            elif t[0] == 'upload_file':
                write_size += int(t[2])
        data_log['read_size'].append(read_size)
        data_log['write_size'].append(write_size)
    for data in interdata_list:
        if data.read_lambda and data.write_lambda:
            data_log['lifetime'].append(data.lifetime)
        data_log['interdata_size'].append(data.size)
    plot_cdf(data_log)       

'''
    Create the csv file of the intermediate data
    name, size, lifetime, write_time, write_lambda
'''

def generate_csv(path, headers, data):
    # get the last name of the path and drop the suffix
    name = os.path.basename(path).split('.')[0]

    with open(path, 'w') as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for d in data:
            if name == 'read':
                writer.writerow({'name': d.name, 'size': d.size, 'read_lambda': d.read_lambda})
            elif name == 'write':
                writer.writerow({'name': d.name, 'size': d.size, 'write_lambda': d.write_lambda})
            elif name == 'life':
                if d.read_lambda and d.write_lambda:
                    writer.writerow({'name': d.name, 'read_num': len(d.read_lambda), 'write_num': len(d.write_lambda), 'lifetime': d.lifetime})


def create_csv():
    global interdata_list
    path = os.path.abspath('.') + '/temp/csv/'
    if not os.path.exists(path):
        os.mkdir(path)
    headers_read = ['name', 'size', 'read_lambda']
    headers_write = ['name', 'size', 'write_lambda']
    headers_life = ['name', 'read_num', 'write_num', 'lifetime']

    generate_csv(path + 'read.csv', headers_read, interdata_list)
    generate_csv(path + 'write.csv', headers_write, interdata_list)
    generate_csv(path + 'life.csv', headers_life, interdata_list)


def empty_dir():
    # get the path of current executing
    path = os.path.abspath('.')
    tmp_path = path + '/temp'
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.mkdir(tmp_path)

def sort_lambda():
    global lambda_list
    global app_start_time
    global app_end_time
    lambda_list = sorted(lambda_list, key=lambda x: x.start_time)
    app_start_time = lambda_list[0].start_time
    app_end_time = lambda_list[-1].upload_end_time[-1]


parse_log(datadir)
for log_entry in myLog:
    print('-----------------Log Start--------------------')
    for t in log_entry:
        print(t)
    print('----------------------------------------------')
empty_dir()
sort_lambda()
create_interdata()

for interdata in interdata_list:
    interdata.compute_lifetime()
    print(interdata.name+' life time: ',interdata.lifetime)


create_cdf(myLog)
create_csv()