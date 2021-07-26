# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 15:01:28 2021

@author: leih31350
"""
# import numpy as np
import pandas as pd
from ftplib import FTP
import os
floats = ['6904096', '6904097', '6904098', '6904099', '6904100', '6904101',
          '6904102', '6904103', '6904104', '6904105']
# floats=['6904096','6904098','6904099','6904100','6904101','6904102',
#         '6904103','6904104','6904105']

# %%
# os.chdir('C:/Users/leih31350/Desktop/SO280/Auslegung/Daten')
os.chdir('H:/SO280/Auslegung/Daten')
ftp = FTP('ftp.ifremer.fr')
ftp.login()
ftp.cwd('ifremer/argo/dac/coriolis/')
folder_content = ftp.nlst()
print(any(x in folder_content for x in floats))
real_floats = []
for i in range(0, len(floats)):
    if floats[i] in folder_content:
        ftp.cwd(floats[i])
        ftp.cwd('profiles')
        real_floats.append(floats[i])
        if not os.path.isdir(floats[i]):
            os.mkdir(floats[i])
        os.chdir(floats[i])
        print('chdir '+floats[i])
        for FILENAME in ftp.nlst():
            if FILENAME not in os.listdir():
                with open(FILENAME, 'wb') as f:
                    ftp.retrbinary('RETR ' + FILENAME, f.write)
                    print('downloading '+FILENAME)
        ftp.cwd('../../')
        os.chdir('../')
ftp.quit()
