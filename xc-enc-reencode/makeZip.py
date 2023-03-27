# to make a zip file of the current directory that contains the vpxenc binary and the excamera-vpxenc.py

import os
import zipfile

def makeZip():
    file_name = ['excamera-xc-enc-reencode.py', 'xc-enc', '/home/handsonhuang/excamera_step_function/Log.py']
    zip_file_name = 'excamera-xc-enc-reencode.zip'
    zip_file = zipfile.ZipFile(zip_file_name, 'w')
    # for file in file_name:
        # zip_file.write(file)
    for file in file_name:
        if file.startswith('/'):
            # just write the file name, not the full path
            zip_file.write(file, os.path.basename(file))
        else:
            zip_file.write(file)
    zip_file.close()
    return zip_file_name

if __name__ == '__main__':
    # makeZip()
    print(makeZip())
    

