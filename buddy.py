# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 14:16:45 2021

@author: bm2187
"""
from argopy import IndexFetcher as ArgoIndexFetcher
from argopy import DataFetcher as ArgoDataFetcher

# obj = ArgoIndexFetcher().float([6902766])
obj = ArgoIndexFetcher().region([-25, -18, 42, 48,
                                  '2021-01-10', '2021-02-12'])

# obj = ArgoIndexFetcher().float([int(x) for x in floats])
                               

# fig, ax = obj.plot()
# fig, ax = obj.plot('trajectory')
fig, ax = obj.plot('dac')
# fig, ax = obj.plot('trajectory', style='white', palette='Set1', figsize=(10,6))