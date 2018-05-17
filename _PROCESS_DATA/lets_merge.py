#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################
## Author: Andrea Marcelli                      ##
## Phd @ Politecnico di Torino                  ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

import argparse
import logging

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

import os
import json
import time
import itertools
from datetime import datetime

THRESHOLD = 30

def assign_wireless_cluster(df_new, df_wireless_cluster, where, idx):
    df_new.loc[where,'wireless_cluster'] = df_wireless_cluster.ix[idx]['HDBSCAN']

def assign_cell_cluster(df_new, df_cell_cluster, where, idx):
    df_new.loc[where,'cell_cluster'] = df_cell_cluster.ix[idx]['HDBSCAN']

def assign_current_place(df_new, df_current_place, where, idx):
    df_new.loc[where,'current_place'] = df_current_place.ix[idx]['value']

def assign_network_traffic(df_new, df_network_traffic, where, idx):
    df_new.loc[where,'total_tx_packets'] = df_network_traffic.ix[idx]['total_tx_packets']

def assign_connectivity(df_new, df_connectivity, where, idx):
    df_new.loc[where,'connected'] = df_connectivity.ix[idx]['connected']
    df_new.loc[where,'network_type'] = df_connectivity.ix[idx]['network_type']

def assign_screen_status(df_new, df_screen, where, idx):
    df_new.loc[where,'screen_status'] = df_screen.ix[idx]['status']

def assign_applications(df_new, df_applications, where, idx):
    df_new.loc[where,'app'] = df_applications.ix[idx]['app']
    df_new.loc[where,'process'] = process = df_applications.ix[idx]['process']

def merge(df_old, df_new, df, assign_function):
    logging.debug("df_new shape : %d", df_new.shape[0])
    logging.debug("df shape: %d", df.shape[0])
    tt = 0

    for t, idx in zip(df['timestamp'].tolist(), list(df.index)):
        if df_old[(df_old['pane_start'] < t) & (df_old['pane_end'] > t)]['pane_start'].any() == True:
            where = df_old[(df_old['pane_start'] < t) & (df_old['pane_end'] > t)]['pane_start'].index[0]
            assign_function(df_new, df, where, idx)
            tt += 1
        else:
            if df_old[(df_old['window_start'] < t) & (df_old['window_end'] > t)]['window_start'].any() == True:
                where = df_old[(df_old['window_start'] < t) & (df_old['window_end'] > t)]['window_start'].index[0]
                assign_function(df_new, df, where, idx)
                tt += 1
            else:
                array_start = np.array(abs(df_old['window_start'] - t))
                min_start = min(array_start)

                array_end = np.array(abs(df_old['window_end'] - t))
                min_end = min(array_end)

                if min_start <= min_end:
                    if min_start/np.power(10,9) <= THRESHOLD:
                        index = np.where(array_start == min_start)[0]
                        tt += 1
                        where = np.where(array_start == min_start)[0]
                        assign_function(df_new, df, where, idx)
                else:
                    if min_end/np.power(10,9) <= THRESHOLD:
                        index = np.where(array_end == min_end)[0]
                        tt += 1
                        where = np.where(array_end == min_end)[0]
                        assign_function(df_new, df, where, idx)

    print("tot matches: %d, %f" % (tt, (tt)/df.shape[0]))


def main():
    ''' That's main! '''
    parser = argparse.ArgumentParser(description='[Unsupervised] Infer user location from CrowdSignals.io dataset')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode on')
    parser.add_argument('-u', '--user', type=int, required=True, help='select to user to work on')

    args = parser.parse_args()
    logging.info("Let's start!")

    if args.debug:
        logging.getLogger().setLevel(level=logging.DEBUG)

    user = args.user

    df_battery =  pd.read_csv("csv/user"+str(user)+"/c-battery.csv", error_bad_lines=False, warn_bad_lines=False)
    df_applications =  pd.read_csv("csv/user"+str(user)+"/c-applications.csv", error_bad_lines=False, warn_bad_lines=False)
    df_connectivity =  pd.read_csv("csv/user"+str(user)+"/c-connectivity.csv", error_bad_lines=False, warn_bad_lines=False)
    df_network_traffic =  pd.read_csv("csv/user"+str(user)+"/c-network_traffic.csv", error_bad_lines=False, warn_bad_lines=False)
    df_screen =  pd.read_csv("csv/user"+str(user)+"/c-screen.csv", error_bad_lines=False, warn_bad_lines=False)

    df_current_place =  pd.read_csv("csv/user"+str(user)+"/s-Current Place.csv", error_bad_lines=False, warn_bad_lines=False)
    df_current_place = df_current_place[df_current_place['viewId'] == 'cp2' ]
    df_current_place.reset_index(inplace=True); del df_current_place['Unnamed: 0']

    df_cell_cluster = pd.read_csv("csv/user"+str(user)+"/df_cell_HDBSCAN.csv", error_bad_lines=False, warn_bad_lines=False)
    df_wireless_cluster = pd.read_csv("csv/user"+str(user)+"/df_wireless_HDBSCAN.csv", error_bad_lines=False, warn_bad_lines=False)

    df_to_process = [df_applications, df_connectivity, df_network_traffic,
                    df_screen, df_current_place, df_cell_cluster, df_wireless_cluster]

    assign_functions = [assign_applications, assign_connectivity, assign_network_traffic,
                        assign_screen_status, assign_current_place, assign_cell_cluster, assign_wireless_cluster]

    df_new = df_battery.copy()
    # Battery
    df_new = df_new.loc[:,['pane_start', 'month', 'day', 'day_of_week', 'hour', 'minute', 'second', 'time_of_day', 'level', 'plugged', 'status',]]
    df_new.rename(columns={'level': 'battery_level', 'status': 'battery_status'}, inplace=True)
    # Applications
    df_new['app'] = np.nan; df_new['process'] = np.nan
    # Connectivity
    df_new['connected'] = np.nan; df_new['network_type'] = np.nan
    # Network Traffic
    df_new['total_tx_packets'] = np.nan
    # Screen
    df_new['screen_status'] = np.nan
    # Current place
    df_new['current_place'] = np.nan
    # Cell clusterer
    df_new['cell_cluster'] = np.nan
    # Wireless clusterer
    df_new['wireless_cluster'] = np.nan

    logging.debug(df_new.columns)

    for df, assign_function in zip(df_to_process, assign_functions):
        merge(df_battery, df_new, df, assign_function)

    logging.debug("Merging finished. Saving result to disk.")
    df_new.to_csv("csv/user"+str(user)+"/df_new.csv")

    # df_new = df_new.dropna()
    # df_new.shape


if __name__ == '__main__':
    # Example usage: ./lets_merge.py -d -u 1
    logging.basicConfig(format='%(asctime)s %(levelname)s:: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(level=logging.INFO)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(message)s'))
    logging.warning(r'© Copyright Andrea Marcelli')
    logging.warning(r'')
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s.%(msecs)04d %(levelname)s:: %(message)s', datefmt='%H:%M:%S'))

    # try:
    main()
    # except Exception as e:
    # 	print('Oops! Something bad happened!')
    # 	print(str(e))
