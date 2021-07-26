# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 14:42:47 2021

@author: bm2187
"""
import xarray as xr
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import datetime
import datetime as dt
import seawater as sw
from matplotlib import gridspec


# %% CTD einlesen
CASTS = pd.DataFrame([['2021-01-12 13:56:28.000', '2021-01-12 23:05:26.000',
                       '2021-01-13 07:04:46.000', '2021-01-13 15:11:58.000'],
                     ['2021-01-12 14:47:54.000', '2021-01-12 23:57:53.000',
                      '2021-01-13 08:14:38.000', '2021-01-13 16:04:22.000'],
                     ['2021-01-12 15:37:22.000', '2021-01-13 00:46:31.000',
                      '2021-01-13 09:10:26.000', '2021-01-13 16:56:41.000']],
                     columns=['03', '05', '07', '09'],
                     index=['start', 'ground', 'end'])
TIMEDELTA={'03':26.8,'05':26.7, '07':26.8, '09':26.8}
# for prof in ['03', '05', '07', '09']:
for prof in ['07']:
    IFILE = ('X:/Meereskunde/Physik/Operationelle Ozeanographie/Seereisen/' +
             'Seereisen_2021/SO280/C-Daten/0'+prof+'_001_ARGOphalti.cnv')

    with open(IFILE, 'r') as f:
        DATUM = f.readlines()
    date = dt.datetime.strptime(DATUM[11][20:-1], '%b %d %Y %H:%M:%S')
    ctd = pd.read_csv(IFILE, skiprows=322, sep='\s+',
                      names=['scan', 'time', 'pressure',
                             'temperature', 'salinity', 'conductivity',
                             'temperature2', 'salinity2', 'conductivity2',
                             'ox1', 'ox2', 'ox3',
                             'fluoro', 'altim', 'flag'],
                      )
    # names=['pressure', 'temperature','conductivity', 'salinity',
    #        'bottles', 'time', 'scan',
    #        'conductivity2', 'flag'])
    # print(ctd.pressure.max())
    if prof == '05':
        ctd = ctd.iloc[2500:-2000]
    else:
        ctd = ctd.iloc[3000:-2000]
    ctd = ctd.astype(float)
    ctd_downcast = ctd.index <= ctd.pressure.nlargest(1).index[0]
    ctd_upcast = ctd.index > ctd.pressure.nlargest(1).index[0]
    ctd_ground = ctd[70900:72700]
    ctd = ctd[ctd_upcast]
    ctd['datetime'] = ctd.time.apply(lambda x: dt.timedelta(seconds=x))+date
    ctd = ctd.set_index(ctd.datetime)
    # data.pres = data.pres - (data.pres.min()-ctd.pressure.min())
    
# %%read rbr file
    ifile = 'H:/SO280/RBR_CTD/60671/0'+prof+'_001_ARGO.txt'
    data = pd.read_csv(ifile, skiprows=13, sep='\s+',
                       names=['0', '1', 'date', 'time', 'nan', 'lat', 'lon',
                              'depth', 'cond', 'temp', 'pres', 'temp2',
                              'disso2', 'correct', 'disso2_sat', 'sea_pres',
                              'psal', 'sound', 'spec_cond', 'dens_anom'])
    # data.pres = data.pres-data.pres[0]
    print(' pressure an bord: ' + str(data.pres[16]))
    # data.pres = data.pres-10.1325
    data.pres = data.pres-data.pres[16]+0.5 # height difference between sensors
    if ifile[-16:-13] == '007':
        start_psal = 6600
        end_psal = -1000
    elif ifile[-16:-13] == '003':
        start_psal = 2600
        end_psal = -1000
    elif ifile[-16:-13] == '005':
        start_psal = 7400
        end_psal = -1000
        data.psal[7049:7053] = np.nan
        # print(i)
    elif ifile[-16:-13] == '009':
        start_psal = 3100
        end_psal = -1000
    # else:
    #     start_psal = data.psal.diff().nlargest(1).index[0]+500
    #     end_psal = data.psal.diff().nlargest(2).index[1]-100
    rbr_pres_max = data.pres.max()
    data = data.iloc[start_psal:end_psal]

    data = data.assign(cast=np.nan)
    data['datetime_str'] = (data.date+' '+data.time)
    data['datetime'] = data.datetime_str.apply(lambda x: dt.datetime.strptime(
                                                    x, '%Y-%m-%d %H:%M:%S.%f')
                                               ) + datetime.timedelta(seconds
                                                   =TIMEDELTA[prof])
    
    data = data.set_index(data.datetime)
    data.index += datetime.timedelta(seconds=26.8)
    # rbr_downcast = data.index <= data.pres.nlargest(1).index[0]
    rbr_downcast = data['2021-01-12 13:56:27.000':
                        '2021-01-12 14:47:54.000'].index
    rbr_upcast = data.index > data.pres.nlargest(1).index[0]
    rbr_ground = data[23600:24150]
    data = data[rbr_upcast]
    data = data.reset_index(drop=True)
    data = pd.merge_asof(data, ctd[['temperature', 'pressure', 'conductivity',
                                    'salinity2']],
                         on='datetime', direction="nearest")
    data = data.set_index(data.datetime)

    # data.index = data.index + datetime.timedelta(seconds=26.8)  # nur '03'
    # %% Correct for C-T lag
    deltat = 0.35  # short-term temperature advance time in seconds
    # advance temperature by deltat to get Tcor
    data['tcor'] = np.interp(pd.to_datetime(data.date+' '+data.time) +
                             dt.timedelta(seconds=deltat),
                             pd.to_datetime(data.date+' '+data.time),
                             data['temp'])

    p = data.pres
    R = data.cond/42.914  # Leitfahigkeit (0,99986)
    R[R < 0] = np.nan

    data['psalcor'] = pd.DataFrame(sw.eos80.salt(R, data.tcor, p),
                                   index=data.index).astype(float)
    psal_new = sw.eos80.salt(R, data.temp, p)
    data['density'] = sw.eos80.dens(psal_new, data.tcor, p)
    data['ptemp'] = sw.eos80.ptmp(psal_new, data.tcor, p, pr=0)
    ctd['ptemp'] = sw.eos80.ptmp(ctd.salinity2, ctd.temperature, ctd.pressure,
                                 pr=0)

    # rbr_ground.cond.plot()
    # ctd_ground.conductivity.plot()
# %% Stabile Stufen
    ctd['stufen'] = np.nan
    data['stufen'] = np.nan
    if prof == '03':
        # lst_stufen = [[4000, 5050], [7900, 9200], [14400, 15950],
        #               [21400, 22800], [28500, 30400], [36500, 37500],
        #               [45000, 46400], [51600, 52900], [58700, 59900]]
        lst_stufen = [[4500, 5050], [8500, 9200], [15100, 15950],
              [21600, 22800], [29700, 30400], [36900, 37500],
              [45900, 46400], [52000, 52900], [59200, 59900]]
    elif prof == '05':
        lst_stufen = [[3500, 4500], [7800, 8300], [11800, 12500],
                      [15500, 16100], [26600, 28200], [37200, 37900],
                      [48700, 49800], [59900, 60800]]
    elif prof == '07':
        # lst_stufen = [[6100, 7500], [13800, 15000], [22500, 24500],
        #               [29000, 30500], [38500, 40000], [46000, 48000],
        #               [53700, 55300], [60700, 62200], 
        #               [76600, 78000]] # sehr kurz [70500, 71600],
        lst_stufen = [[6100, 7500], [13900, 14800], [23400, 24500],
              [29700, 30500], [39300, 40000], [46800, 47800],
              [53800, 55300], [61000, 62200], 
              [76900, 78000]] # sehr kurz [70500, 71600],
    elif prof == '09':
        lst_stufen = [[2900, 4500], [7200, 8500], [11500, 13000],
                      [18500, 19500], [27200, 29200], [33000, 34700],
                      [45500, 47000], [52500, 54000], [63000, 64500]]
    str_stufen = []
    int_stufen = []
    a = 1
    for i, j in reversed(lst_stufen):
        ctd.iloc[i:j, ctd.columns.get_loc('stufen')] = a
        data.iloc[(data.index >= ctd[ctd.stufen == a].index[0]) &
                  (data.index <= ctd[ctd.stufen == a].index[-1]),
                  data.columns.get_loc('stufen')] = a
        int_stufen.append(ctd.pressure.iloc[i:j].mean().round(0))
        str_stufen.append(str(ctd.pressure.iloc[i:j].mean().round(0)))
        # print(a, i, j)
        a += 1
        
    if data.stufen.value_counts().min()<=150:
        print('!!!einige Stufen zu kurz!!!')
# %%
    plt.figure()
    ctd.pressure.plot()
    ctd[ctd.stufen > 0].pressure.plot(marker='.', linestyle='none',
                                      ylabel='pressure[dbar]')
    plt.title('stops prof'+ str(prof))
    plt.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/Stufen_prof'+prof+'.png')
# %% figure je Stufe
    
    for st in reversed(ctd.stufen.dropna().unique()):
        plt.figure()
    
        fig, axes = plt.subplots(2,2,figsize=[15,8])
        fig.suptitle(str(ctd.pressure[ctd.stufen == st].mean().round(0))+' dbar prof'+prof)
        axes[0, 0].plot(ctd.pressure[ctd.stufen == st])
        axes[0, 0].plot(data[data.stufen == st].pres)
        axes[0, 0].grid()
        axes[0 ,0].set_ylabel('pressure[dbar]')
        plt.setp(axes[0, 0].get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
    
        axes[0, 1].plot(ctd.temperature[ctd.stufen == st])
        axes[0, 1].plot(data[data.stufen == st].temp)
        axes[0, 1].grid()
        axes[0 ,1].set_ylabel('temperature[°C]')
        plt.setp(axes[0, 1].get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
    
        axes[1, 0].plot(ctd.conductivity[ctd.stufen == st])
        axes[1, 0].plot(data[data.stufen == st].cond)
        axes[1, 0].grid()
        axes[1 ,0].set_ylabel('conductivity')
        plt.setp(axes[1, 0].get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
    
        axes[1, 1].plot(ctd.salinity2[ctd.stufen == st])
        axes[1, 1].plot(data[data.stufen == st].psalcor)
        axes[1, 1].grid()
        axes[1, 1].legend(['ctd', 'rbr_corrected'])
        plt.setp(axes[1, 1].get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        axes[1 ,1].set_ylabel('salinity [PSU]')
        plt.tight_layout()
        plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_st'+str(int(st))+'.png')
    
    # %% mit profil
    for st in reversed(ctd.stufen.dropna().unique()):
        plt.close('all')
        fig = plt.figure(1, figsize=[15,8])
        fig.suptitle(str(ctd.pressure[ctd.stufen == st].mean().round(0))+' dbar prof'+prof)
        # set up subplot grid
        gridspec.GridSpec(2,3)
        plt.subplot2grid((2,3), (0,2), colspan=1, rowspan=2)
        plt.plot(ctd.salinity2, -ctd.pressure)
        plt.plot(data[:-700].psal, -data[:-700].pres)
        plt.plot(ctd[ctd.stufen == st].salinity2,
                 -ctd[ctd.stufen == st].pressure,
                 marker='.',
                 markersize=20,
                 linestyle='none')
        plt.xlabel('salinity [PSU]')
        plt.ylabel('pressure[dbar')
        plt.legend(['ctd','rbr'])
        
        
        plt.subplot2grid((2,3), (0,0))
        plt.plot(ctd.pressure[ctd.stufen == st])
        plt.plot(data[data.stufen == st].pres)
        plt.grid()
        plt.ylabel('pressure[dbar]')
        plt.setp(plt.gca().get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
        
        plt.subplot2grid((2,3), (0,1))
        plt.plot(ctd.temperature[ctd.stufen == st])
        plt.plot(data[data.stufen == st].temp)
        plt.grid()
        plt.ylabel('temperature[°C]')
        plt.setp(plt.gca().get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
        
        plt.subplot2grid((2,3), (1,0))
        plt.plot(ctd.conductivity[ctd.stufen == st])
        plt.plot(data[data.stufen == st].cond)
        plt.grid()
        plt.ylabel('conductivity')
        plt.setp(plt.gca().get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.tight_layout()
        
        plt.subplot2grid((2,3), (1,1))
        plt.plot(ctd.salinity2[ctd.stufen == st])
        plt.plot(data[data.stufen == st].psalcor)
        plt.grid()
        plt.legend(['ctd', 'rbr_corrected'])
        plt.setp(plt.gca().get_xticklabels(), rotation=30,
                 horizontalalignment='right')
        plt.ylabel('salinity [PSU]')
        plt.tight_layout()
        plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                str(prof)+'_st'+str(int(st))+'_mit_psal_profil.png')
    # %% figure je variable
    fig = plt.figure(figsize=[20,10])
    # plt.title('Pressure')
    position=[1,2,3,5,6,7,9,10,11]
    for st in reversed(ctd.stufen.dropna().unique()):
        st = int(st)
        ax = fig.add_subplot(3, 4, position[st-1])
        ax.plot(ctd.pressure[ctd.stufen == st])
        ax.plot(data[data.stufen == st].pres)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0)) + ' dbar')
        ax.grid()
        ax.set_ylabel('pressure [dbar]')
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()
    ax1 = fig.add_subplot(1,4,4)
    ax1.plot(ctd.salinity2, -ctd.pressure)
    ax1.plot(data[:-500].psal, -data[:-500].pres)
    # ax1.set_xlabel('pot. temperature [°C]')
    ax1.set_xlabel('salinity [PSU]')
    ax1.set_ylabel('pressure [dbar]')
    ax1.plot(data.psal[data.stufen>0], -data.pres[data.stufen>0],
             linestyle='none', marker = '.')
    [ax1.axhline(y=-x) for x in int_stufen]          
    plt.legend(['ctd', 'rbr'])
    fig.suptitle('pressure prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_pres.png')
    
    fig = plt.figure(figsize=[20,10])
    # plt.title('Temperature')
    for st in ctd.stufen.dropna().unique():
        st = int(st)
    
        ax = fig.add_subplot(3, 4, position[st-1])
        ax.plot(ctd.temperature[ctd.stufen == st])
        ax.plot(data[data.stufen == st].temp)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0))+ ' dbar')
        ax.set_ylabel('temperature [°C]')
        ax.grid()
        plt.tight_layout()
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    ax1 = fig.add_subplot(1,4,4)
    ax1.plot(ctd.salinity2, -ctd.pressure)
    ax1.plot(data[:-500].psal, -data[:-500].pres)
    # ax1.set_xlabel('pot. temperature [°C]')
    ax1.set_xlabel('salinity [PSU]')
    ax1.set_ylabel('pressure [dbar]')
    ax1.plot(data.psal[data.stufen>0], -data.pres[data.stufen>0],
             linestyle='none', marker = '.')
    [ax1.axhline(y=-x) for x in int_stufen]  
        # fig.autofmt_xdate()
    plt.legend(['ctd', 'rbr'])
    fig.suptitle('temperature prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_temp.png')
        
    fig = plt.figure(figsize=[20,10]) 
    # plt.title('Conductivity')   
    for st in ctd.stufen.dropna().unique():
        st = int(st)
        ax = fig.add_subplot(3,4, position[st-1])
        ax.plot(ctd.conductivity[ctd.stufen == st])
        ax.plot(data[data.stufen == st].cond)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0))+ ' dbar')
        ax.set_ylabel('conductivity[mS/cm]')
        ax.grid()
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()
    ax1 = fig.add_subplot(1,4,4)
    ax1.plot(ctd.salinity2, -ctd.pressure)
    ax1.plot(data[:-500].psal, -data[:-500].pres)
    # ax1.set_xlabel('pot. temperature [°C]')
    ax1.set_xlabel('salinity [PSU]')
    ax1.set_ylabel('pressure [dbar]')
    ax1.plot(data.psal[data.stufen>0], -data.pres[data.stufen>0],
             linestyle='none', marker = '.')
    [ax1.axhline(y=-x) for x in int_stufen]  
    plt.legend(['ctd', 'rbr'])
    fig.suptitle('conductivity prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_cond.png')
    
    fig = plt.figure(figsize=[20,10]) 
    for st in ctd.stufen.dropna().unique():
        st = int(st)
        ax = fig.add_subplot(3, 4, position[st-1])
        ax.plot(ctd.salinity2[ctd.stufen == st])
        ax.plot(data[data.stufen == st].psalcor)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0))+ ' dbar')
        ax.set_ylabel('salinity [PSU]')
        ax.grid()
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()
    ax1 = fig.add_subplot(1,4,4)
    ax1.plot(ctd.salinity2, -ctd.pressure)
    ax1.plot(data[:-500].psal, -data[:-500].pres)
    # ax1.set_xlabel('pot. temperature [°C]')
    ax1.set_xlabel('salinity [PSU]')
    ax1.set_ylabel('pressure [dbar]')
    ax1.plot(data.psal[data.stufen>0], -data.pres[data.stufen>0],
             linestyle='none', marker = '.')
    [ax1.axhline(y=-x) for x in int_stufen]  
    plt.legend(['ctd', 'rbr_corrected'])
    fig.suptitle('salinity prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_psal.png')
    
    # %% HIST figure je variable
    fig = plt.figure(figsize=[20,10])
    # plt.title('Pressure')
    for st in reversed(ctd.stufen.dropna().unique()):
        st = int(st)
        ax = fig.add_subplot(3, 4, position[st-1])
        ax.hist(ctd.pressure[ctd.stufen == st])
        ax.hist(data[data.stufen == st].pres)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0)) + ' dbar')
        ax.grid()
        ax.set_xlabel('pressure [dbar]')
        # plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()
    plt.legend(['ctd','rbr'])
    fig.suptitle('pressure prof'+prof)    
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_hist_pres.png')
        
    fig = plt.figure(figsize=[20,10])
    # plt.title('Temperature')
    for st in reversed(ctd.stufen.dropna().unique()):
        st = int(st)
        
        ax = fig.add_subplot(3,3,st)
        ax.hist(ctd.temperature[ctd.stufen == st])
        ax.hist(data[data.stufen == st].temp)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0))+ ' dbar')
        ax.set_xlabel('temperature [°C]')
        ax.grid()
        plt.tight_layout()
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        # fig.autofmt_xdate()
    plt.legend(['ctd','rbr'])
    fig.suptitle('temperature prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_hist_temp.png')
        
    fig = plt.figure(figsize=[20,10]) 
    # plt.title('Conductivity')   
    for st in reversed(ctd.stufen.dropna().unique()):
        st = int(st)
        ax = fig.add_subplot(3,3,st)
        ax.hist(ctd.conductivity[ctd.stufen == st])
        ax.hist(data[data.stufen == st].cond)
        ax.set_title(str(ctd.pressure[ctd.stufen == st].mean().round(0))+ ' dbar')
        ax.set_xlabel('conductivity')
        ax.grid()
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()
    plt.legend(['ctd','rbr'])
    fig.suptitle('conductivity prof'+prof)
    fig.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_hist_cond.png')
    
    # %% mean diff und std von diff
    plt.figure()
    
    fig, axes = plt.subplots(2,2,figsize=[15,8])
    fig.suptitle('Mean diff + std of diff prof'+prof)
    
    data['pres_diff'] = (data.pres - data.pressure)
    diff_des = data.groupby('stufen').pres_diff.describe()
    axes[0, 0].plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    axes[0, 0].errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    axes[0, 0].set_xlabel('pressure [dbar]')
    axes[0, 0].set_ylabel('pressure [$\Delta$dbar]')
    
    data['temp_diff'] = (data.temp - data.temperature)
    diff_des = data.groupby('stufen').temp_diff.describe()
    axes[0, 1].plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    axes[0, 1].errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    # plt.setp(axes,ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    axes[0, 1].set_xlabel('pressure [dbar]')
    axes[0, 1].set_ylabel('temperature [$\Delta$°C]')
    
    data['cond_diff'] = (data.cond - data.conductivity)
    diff_des = data.groupby('stufen').cond_diff.describe()
    axes[1, 0].plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    axes[1, 0].errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    axes[1, 0].set_xlabel('pressure [dbar]')
    axes[1, 0].set_ylabel('conductivity [$\Delta$mS/cm]')
    
    
    data['psal_diff'] = (data.psalcor - data.salinity2)
    diff_des = data.groupby('stufen').psal_diff.describe()
    axes[1, 1].plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    axes[1, 1].errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    axes[1, 1].set_xlabel('pressure [dbar]')
    axes[1, 1].set_ylabel('salinity [$\Delta$PSU]')
    plt.setp(axes, xticks=ctd.stufen.dropna().unique(), xticklabels=str_stufen)
    plt.tight_layout()
    plt.savefig('H://SO280/Auslegung/figures/Stufen/RBR_CTD_prof'+
                    str(prof)+'_diff_std.png')
    
    # # %%
    # plt.figure()
    # data['pres_diff'] = (data.pres - data.pressure)
    # diff_des = data.groupby('stufen').pres_diff.describe()
    # plt.plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    # plt.errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    # plt.xlabel('pressure [dbar]')
    # plt.ylabel('pressure [$\Delta$dbar]')
    
    # plt.figure()
    # data['cond_diff'] = (data.cond - data.conductivity)
    # diff_des = data.groupby('stufen').cond_diff.describe()
    # plt.plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    # plt.errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    # plt.xlabel('pressure [dbar]')
    # plt.ylabel('conductivity [$\Delta$mS/cm]')
    
    
    # plt.figure()
    # data['psal_diff'] = (data.psalcor - data.salinity2)
    # diff_des = data.groupby('stufen').psal_diff.describe()
    # plt.plot(ctd.stufen.dropna().unique(), diff_des['mean'], marker='.')
    # plt.errorbar(ctd.stufen.dropna().unique(), diff_des['mean'], diff_des['std'])
    # plt.xticks(ctd.stufen.dropna().unique(), str_stufen, rotation=30)
    # plt.xlabel('pressure [dbar]')
    # plt.ylabel('salinity [$\Delta$PSU]')
    
    # %%
    # plt.grid()
    # plt.plot([33,43],[33,43],color='red')
    # plt.scatter(data.cond,data.conductivity
    #             ,marker='.', c ='.3')
    # plt.xlim([33,43])
    
