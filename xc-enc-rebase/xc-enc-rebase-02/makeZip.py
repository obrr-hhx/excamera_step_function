# to make a zip file of the current directory that contains the vpxenc binary and the excamera-vpxenc.py

import os
import zipfile

# get the curret path
current_path = os.path.dirname(os.path.abspath(__file__)) + '/'

def makeZip():
    file_name = [current_path+'excamera-xc-enc-rebase-02.py', current_path+'xc-enc', current_path+'../../Log.py']
    zip_file_name = current_path+'excamera-xc-enc-rebase-02.zip'
    zip_file = zipfile.ZipFile(zip_file_name, 'w')
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
    

