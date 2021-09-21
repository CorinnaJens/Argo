# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 10:24:12 2021

@author: bm2187
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import xarray as xr


# %% Float einlesen
os.chdir('H:/SO280/Auslegung/Daten')
# floats = ['6904096', '6904097', '6904098', '6904099', '6904100', '6904102',
#           '6904103', '6904104', '6904105']
floats = ['6904096', '6904098', '6904099', '6904100',
          '6904102', '6904103', '6904104', '6904105']
# floats=['6904096','6904099','6904100',
#         '6904103','6904104']
profiles = ['_045']
rbr = floats[4:]
sbe = floats[:4]
locations = pd.DataFrame()

temp_profiles = pd.DataFrame()
pres_profiles = pd.DataFrame()
psal_profiles = pd.DataFrame()
loc = pd.DataFrame()

for i, fl in enumerate(floats):
    os.chdir('H:/SO280/Auslegung/Daten/'+fl)
    lat = []
    lon = []
    print(fl)
    for file in ['R'+fl + x+'.nc' for x in profiles]:
        IFILE = file
        ds = xr.open_dataset(IFILE)
        df = ds.to_dataframe()
        df = df.loc[0, 0, :, 0, 0].reset_index()  # Choose only first profile
        if file == 'R6904096_018.nc':
            print('Fehlerhafter File '+file)
            pres_profiles[int(file[10:12]), fl] = np.nan
            temp_profiles[int(file[10:12]), fl] = np.nan
            psal_profiles[int(file[10:12]), fl] = np.nan
            pass
        elif file == 'R6904100_030.nc':
            print('Fehlerhafter File '+file)
            pres_profiles[int(file[10:12]), fl] = np.nan
            temp_profiles[int(file[10:12]), fl] = np.nan
            psal_profiles[int(file[10:12]), fl] = np.nan
        else:
            df.loc[df.TEMP_QC.astype('int') >= 2,'TEMP'] = np.nan
            df.loc[df.PSAL_QC.astype('int') >= 2,'PSAL'] = np.nan
            df.loc[df.PRES_QC.astype('int') >= 2,'PRES'] = np.nan
            locations[fl] = [df.LATITUDE[0], df.LONGITUDE[0]]
            if (file[12] != 'D'):
                locations['prof'] = int(file[10:12])
                lon.append(df.LONGITUDE[0])
                lat.append(df.LATITUDE[0])
                pres_profiles[int(file[10:12]), fl] = df.PRES
                temp_profiles[int(file[10:12]), fl] = df.TEMP
                psal_profiles[int(file[10:12]), fl] = df.PSAL

            # plt.figure(int(file[10:12]),figsize=[20,10])
            # if fl in rbr:
            #     plt.plot(df.TEMP,-df.PRES,color='r')

            # elif fl in sbe:
            #     plt.plot(df.TEMP,-df.PRES,color='b')
            #     plt.xlabel('temperature [°C]')
            #     plt.ylabel('pressure [dbar]')
            # if fl in rbr:
            #     plt.plot(df.PSAL,-df.PRES,color='r')

            # elif fl in sbe:
            #     plt.plot(df.PSAL,-df.PRES,color='b')
            #     plt.xlabel('salinity [PSU]')
            #     plt.ylabel('pressure [dbar]')
    # if (fl == '6904099'):
    #     lat.insert(33, np.nan)
    #     lon.insert(33, np.nan)

    loc[('lat', fl)] = lat
    loc[('lon', fl)] = lon
# pres_profiles[33, '6904099'] = np.nan
# temp_profiles[33, '6904099'] = np.nan
# psal_profiles[33, '6904099'] = np.nan

loc.columns = pd.MultiIndex.from_tuples(loc.columns)
pres_profiles.columns = pd.MultiIndex.from_tuples(pres_profiles.columns)
psal_profiles.columns = pd.MultiIndex.from_tuples(psal_profiles.columns)
temp_profiles.columns = pd.MultiIndex.from_tuples(temp_profiles.columns)
# %% Plot
plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(psal_profiles[i][sbe], -pres_profiles[i][sbe], color='b')
    plt.plot(psal_profiles[i][rbr], -pres_profiles[i][rbr], color='r')
    plt.title('IceDivA floats swarm, salinity whole profile cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('pressure [dbar]')
    plt.xlim([34.85, 35.85])
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_cycl'+str(i)+'.png')

plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(temp_profiles[i][sbe], -pres_profiles[i][sbe], color='b')
    plt.plot(temp_profiles[i][rbr], -pres_profiles[i][rbr], color='r')
    plt.title('IceDivA floats swarm, temperature whole profile cycle '+str(i))

    plt.xlabel('temperature [°C]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_temp_cycl'+str(i)+'.png')

# %% Plot deep
plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(psal_profiles[pres_profiles >= 1500][i][sbe],
             -pres_profiles[pres_profiles >= 1500][i][sbe],
             color='b')
    plt.plot(psal_profiles[pres_profiles >= 1500][i][rbr],
             -pres_profiles[pres_profiles >= 1500][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, salinity 1500-max dbar depth cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_deep_cycl'+str(i)+'.png')

plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(temp_profiles[pres_profiles >= 1500][i][sbe],
             -pres_profiles[pres_profiles >= 1500][i][sbe],
             color='b')
    plt.plot(temp_profiles[pres_profiles >= 1500][i][rbr],
             -pres_profiles[pres_profiles >= 1500][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, temperature 1500-max dbar depth cycle '+str(i))

    plt.xlabel('temperature [°C]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_temp_deep_cycl'+str(i)+'.png')
#100m
    plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(psal_profiles[pres_profiles >= 1900][i][sbe],
             -pres_profiles[pres_profiles >= 1900][i][sbe],
             color='b')
    plt.plot(psal_profiles[pres_profiles >= 1900][i][rbr],
             -pres_profiles[pres_profiles >= 1900][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, salinity 1900-max dbar depth cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('pressure [dbar]')
    plt.ylim(-2000, -1900)
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_deep_100m_cycl'+str(i)+'.png')

plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(temp_profiles[pres_profiles >= 1900][i][sbe],
             -pres_profiles[pres_profiles >= 1900][i][sbe],
             color='b')
    plt.plot(temp_profiles[pres_profiles >= 1900][i][rbr],
             -pres_profiles[pres_profiles >= 1900][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, temperature 1900-max dbar depth cycle '+str(i))

    plt.xlabel('temperature [°C]')
    plt.ylabel('pressure [dbar]')
    plt.ylim(-2000, -1900)
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_temp_deep_100m_cycl'+str(i)+'.png')

# %% Plot shallow
plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(psal_profiles[pres_profiles <= 250][i][sbe],
             -pres_profiles[pres_profiles <= 250][i][sbe],
             color='b')
    plt.plot(psal_profiles[pres_profiles <= 250][i][rbr],
             -pres_profiles[pres_profiles <= 250][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, salinity 0-250 dbar depth cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_shallow_cycl'+str(i)+'.png')

plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(temp_profiles[pres_profiles <= 250][i][sbe],
             -pres_profiles[pres_profiles <= 250][i][sbe],
             color='b')
    plt.plot(temp_profiles[pres_profiles <= 250][i][rbr],
             -pres_profiles[pres_profiles <= 250][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, temperature 0-250 dbar depth cycle '+str(i))

    plt.xlabel('temperature [°C]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_temp_shallow_cycl'+str(i)+'.png')


# %% oberste 10 m
plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.scatter(psal_profiles[pres_profiles < 10][i][sbe],
                -pres_profiles[pres_profiles < 10][i][sbe],
                color='b')
    plt.plot(psal_profiles[pres_profiles < 10][i][sbe],
             -pres_profiles[pres_profiles < 10][i][sbe],
             color='b')
    plt.scatter(psal_profiles[pres_profiles < 10][i][rbr],
                -pres_profiles[pres_profiles < 10][i][rbr],
                color='r')
    plt.plot(psal_profiles[pres_profiles < 10][i][rbr],
             -pres_profiles[pres_profiles < 10][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, salinity 0-10 dbar depth cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_10m_cycl'+str(i)+'.png')

    plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.scatter(temp_profiles[pres_profiles < 10][i][sbe],
                -pres_profiles[pres_profiles < 10][i][sbe],
                color='b')

    plt.plot(temp_profiles[pres_profiles < 10][i][sbe],
             -pres_profiles[pres_profiles < 10][i][sbe],
             color='b')
    plt.scatter(temp_profiles[pres_profiles < 10][i][rbr],
                -pres_profiles[pres_profiles < 10][i][rbr],
                color='r')
    plt.plot(temp_profiles[pres_profiles < 10][i][rbr],
             -pres_profiles[pres_profiles < 10][i][rbr],
             color='r')
    plt.title('IceDivA floats swarm, temperature 0-10 dbar depth cycle '+str(i))
    
    plt.xlabel('temperature [°C]')
    plt.ylabel('pressure [dbar]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_temp_10m_cycl'+str(i)+'.png')
# %% Plot psal temp
plt.close('all')
for i in profiles:
    i=int(i[1:4])
    plt.figure(i, figsize=[8, 5])
    plt.plot(psal_profiles[i][sbe], temp_profiles[i][sbe], color='b')
    plt.plot(psal_profiles[i][rbr], temp_profiles[i][rbr], color='r')
    plt.title('IceDivA floats swarm, temperature/salinity cycle '+str(i))

    plt.xlabel('salinity [PSU]')
    plt.ylabel('temperature [°C]')
    plt.legend(floats)
    plt.tight_layout()
    plt.savefig('../../figures/Vortrag/floats_psal_temp_cycl'+str(i)+'.png')


# # %%
# plt.figure(1, figsize=[20,10])
# for i in range(1,8):
#     plt.scatter(psal_profiles[i][rbr], temp_profiles[i][rbr],0.5, color='r')
#     plt.scatter(psal_profiles[i][sbe], temp_profiles[i][sbe],0.5, color='b')
# %%

plt.figure(2, figsize=[8, 5])
for fl in floats:
    plt.text(loc['lon'][fl].iloc[-1], loc['lat'][fl].iloc[-1], fl)
plt.scatter(loc['lon'][sbe].iloc[-1], loc['lat'][sbe].iloc[-1], color='b')
plt.scatter(loc['lon'][rbr].iloc[-1], loc['lat'][rbr].iloc[-1], color='r')
plt.title('IceDivA floats swarm last location, cycle '+profiles[0][1:])
plt.tight_layout()
plt.savefig('../../figures/Vortrag/floats_lastloc.png')
# %%

plt.figure(3, figsize=[8, 5])

for fl in floats:
    plt.text(loc['lon'][fl].iloc[-1], loc['lat'][fl].iloc[-1], fl)
plt.scatter(loc['lon'].iloc[-1], loc['lat'].iloc[-1],
            c=psal_profiles[pres_profiles.round()==10].dropna(how='all'
                                                               ).mean()
           )

# plt.scatter(loc['lon'][rbr].iloc[-1], loc['lat'][rbr].iloc[-1], color='r')
plt.title('IceDivA floats swarm locationsalinity at 10m depth, profile '+profiles[0][1:])
plt.colorbar()
plt.tight_layout()

# %% Test
# IFILE='E:/CMEMS/global-analysis-forecast-phy-001-024_20210711_20210711.nc'
# ds = xr.open_dataset(IFILE)
# psal_ref_diff = pd.DataFrame()

# for fl in floats:
#     psal_ref_diff[fl] =((psal_profiles[pres_profiles.round()==6].dropna(how='all').mean()[42][fl]
#       ) - (ds.so.sel(latitude=loc['lat'][fl].iloc[-1],
#                       longitude=loc['lon'][fl].iloc[-1],
#                       method='nearest').values))[0]
#     plt.text(loc['lon'][fl].iloc[-1], loc['lat'][fl].iloc[-1], fl)                 
                      
# ds.so[:,:,(ds.latitude>=44) & (ds.latitude<=46),
#         (ds.longitude>=-25) &(ds.longitude<=-19)
#         ].plot(levels=np.arange(35.5,36,0.1))
# plt.scatter(loc['lon'].iloc[-1], loc['lat'].iloc[-1],
#             c=psal_ref_diff.transpose(),cmap='bwr', vmin=-0.1, vmax=0.1)
# plt.colorbar()
# # plt.savefig('../../figures/Vortrag/floats_forecast_diff.png')