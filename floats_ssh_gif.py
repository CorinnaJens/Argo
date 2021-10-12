# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:06:19 2021

@author: leih31350
"""
# %% Set basics
import os
import xarray as xr
from ftplib import FTP
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imageio

# %% Float einlesen
os.chdir('H:/SO280/Auslegung/Daten')
# floats=['6904096','6904097','6904098','6904099','6904100','6904102',
#         '6904103','6904104','6904105']
floats = ['6904096', '6904098', '6904099', '6904100',
          '6904102', '6904103', '6904104', '6904105']
rbr = floats[4:]
sbe = floats[:4]
locations = pd.DataFrame()

temp_profiles = pd.DataFrame()
pres_profiles = pd.DataFrame()
psal_profiles = pd.DataFrame()
loc = pd.DataFrame()
for i, fl in enumerate(floats):
    os.chdir('H:/SO280/Auslegung/Daten/'+fl)
    lat =[]
    lon = []
    for file in os.listdir():
        IFILE = file
        ds = xr.open_dataset(IFILE)
        df = ds.to_dataframe()
        df = df.loc[0, 0, :, 0, 0].reset_index()  # Choose only first profile
        locations[fl]=[df.LATITUDE[0],df.LONGITUDE[0]]
        if file[12] != 'D':
            locations['prof']=int(file[10:12])
            lon.append(df.LONGITUDE[0])
            lat.append(df.LATITUDE[0])
    if (fl == '6904097'):
        lat.insert(18, np.nan)
        lon.insert(18, np.nan)
    # if (fl == '6904100'):
    #     lat.insert(30, np.nan)
    #     lon.insert(30, np.nan)
    loc[('lat', fl)] = lat
    loc[('lon', fl)] = lon
loc.columns = pd.MultiIndex.from_tuples(loc.columns)

# %% CMEMs einlesen
d_lon = -21  # deployment position
d_lat = 45.5
lat_bnds = [48, 45, 42, 39, 36]     # planned working areas
lon_bnds = [-19, -19, -19, -19, -19]
filenames = []
filenames2 = []
dates = ['0114', '0116', '0118', '0120', '0122', '0124', '0126', '0128',
         '0130', '0201', '0203', '0205', '0207', '0209', '0211', '0213',
         '0215', '0217', '0219', '0221', '0223', '0225', '0227',
         '0301', '0303', '0305', '0307', '0309', '0311', '0313', '0323',
         '0402', '0412', '0422', '0502', '0512', '0522', '0601', '0611',
         '0621', '0701', '0711', '0721', '0731', '0810', '0820', '0830',
         '0909']
for i, date in enumerate(dates):
    fname = ('E:/CMEMS/' +
             'nrt_europe_allsat_phy_l4_2021'+date+'_2021'+date+'.nc')
    ds = xr.open_dataset(fname)
    plt.close('all')
    print('plotting: '+fname)
# %%Plot SSH

    fig = plt.figure(1, figsize=[10, 5])
    ds.adt[0, (ds.latitude > 43) & (ds.latitude < 49),
              (ds.longitude < -15) & (ds.longitude > -25)
           ].plot(levels=np.arange(-0.35, 0.35, 0.01)) #ssh
    fig, axes = plt.plot(d_lon, d_lat, 1, marker='+') #deployment position
    plt.scatter(lon_bnds, lat_bnds, marker='*',
                s=[50 for i in range(len(lon_bnds))]) #planned working areas
    plt.scatter([d_lon, d_lon+7/60, d_lon+7/60, d_lon-7/60, d_lon-7/60],
                [d_lat, d_lat+7/60, d_lat-7/60, d_lat+7/60, d_lat-7/60, ],
                1, marker='*', c='k')
    plt.tight_layout()
    
# %% Plot traj    
    plt.plot(loc['lon'][:i],loc['lat'][:i])
    plt.scatter(loc['lon'][:i],loc['lat'][:i])
    # for i in range(0,len(loc)):
    plt.scatter(loc['lon'][rbr].iloc[i],loc['lat'][rbr].iloc[i],color='r')
    plt.scatter(loc['lon'][sbe].iloc[i],loc['lat'][sbe].iloc[i],color='b')
    plt.legend(floats)
    plt.tight_layout()
    
    plt.tight_layout()
    plt.savefig('../../figures/floats_ssh'+str(int(ds.time.dt.strftime('%Y%m%d')))+'.png')
    filenames.append('../../figures/floats_ssh'+str(int(ds.time.dt.strftime('%Y%m%d')))+'.png')
# %%Plot SSH close
    fig = plt.figure(2, figsize=[10, 5])
    ds.adt[0, (ds.latitude > 43) & (ds.latitude < 47.5),
              (ds.longitude < -18.5) & (ds.longitude > -24.5)
           ].plot(levels=np.arange(-0.35, 0.35, 0.01))
    fig, axes = plt.plot(d_lon, d_lat, 1, marker='+')
    # plt.scatter(lon_bnds, lat_bnds, marker='.',
                # s=[50 for i in range(len(lon_bnds))])
    plt.scatter([d_lon, d_lon+7/60, d_lon+7/60, d_lon-7/60, d_lon-7/60],
                [d_lat, d_lat+7/60, d_lat-7/60, d_lat+7/60, d_lat-7/60, ],
                1, marker='*', c='k')
    plt.tight_layout()
        
# %% Plot traj 2
    plt.plot(loc['lon'][:i],loc['lat'][:i])
    plt.scatter(loc['lon'][:i],loc['lat'][:i], color='orange')
    # for i in range(0,len(loc)):
    plt.scatter(loc['lon'][rbr].iloc[i],loc['lat'][rbr].iloc[i],color='r')
    plt.scatter(loc['lon'][sbe].iloc[i],loc['lat'][sbe].iloc[i],color='b')
    plt.legend(floats)
    plt.tight_layout()
    
    plt.tight_layout()
    plt.savefig('../../figures/floats_ssh_closeup'+str(int(ds.time.dt.strftime('%Y%m%d')))+'.png')
    filenames2.append('../../figures/floats_ssh_closeup'+str(int(ds.time.dt.strftime('%Y%m%d')))+'.png')

# %% Append to gif
with imageio.get_writer('../../figures/mygif.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)
print('gif erstellt')
# %%
with imageio.get_writer('../../figures/floats_ssh_closeup.gif', mode='I', fps=5) as writer:
    for filename in filenames2:
        image = imageio.imread(filename)
        writer.append_data(image)
    writer.append_data(image)
    writer.append_data(image)
    writer.append_data(image)
    writer.append_data(image)
    writer.append_data(image)
    writer.append_data(image)
print('gif erstellt')

# %% GIF von Profilen
# #psal
# with imageio.get_writer('../../figures/psal_profiles.gif', mode='I') as writer:
#     for cyc in range(1, 22):
#         filename = ('H:/SO280/Auslegung/figures/Vortrag/floats_psal_cycl'+str(cyc)+'.png')
#         image = imageio.imread(filename)
#         writer.append_data(image)
# print('psal profiles gif erstellt')

# #temp
# with imageio.get_writer('../../figures/temp_profiles.gif', mode='I') as writer:
#     for cyc in range(1, 22):
#         filename = ('H:/SO280/Auslegung/figures/Vortrag/floats_temp_cycl'+str(cyc)+'.png')
#         image = imageio.imread(filename)
#         writer.append_data(image)
# print('temp profiles gif erstellt')
