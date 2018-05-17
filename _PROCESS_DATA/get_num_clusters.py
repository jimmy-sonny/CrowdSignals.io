#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################
## Author: Andrea Marcelli                      ##
## Ph.D. @ Politecnico di Torino                ##
## andrea.marcelli@polito.it                    ##
## 05/11/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

import argparse
import logging

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np


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
    df_w = None; df_c = None;

    logging.info("Reading Data Frame wireless...")
    df_w = pd.read_csv("csv/user"+str(user)+"/df_wireless_HDBSCAN.csv", index_col=0)
    # print("wireless", df_w.groupby(['month','day_of_week','hour']).count()['timestamp'].values.shape)
    logging.info("Reading Data Frame cellular...")
    df_c = pd.read_csv("csv/user"+str(user)+"/df_cell_HDBSCAN.csv", index_col=0)
    # print("cell", df_c.groupby(['month','day_of_week','hour']).count()['timestamp'].values.shape)

    kkw = set([k for k, _ in df_w.groupby(['month','day_of_week','hour'])])
    kkc = set([k for k, _ in df_c.groupby(['month','day_of_week','hour'])])
    kk = kkc & kkw

    num_cw = set()
    num_cc = set()
    for k in kk:
        num_cw.update(df_w.groupby(['month','day_of_week','hour']).get_group(k)['HDBSCAN'].values)
        num_cc.update(df_c.groupby(['month','day_of_week','hour']).get_group(k)['HDBSCAN'].values)

    print("wireless", len(num_cw), num_cw)
    print("cell", len(num_cc), num_cc)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(level=logging.INFO)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(message)s'))
    logging.warning(r'© Copyright Andrea Marcelli')
    logging.warning(r'')
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s.%(msecs)04d %(levelname)s:: %(message)s', datefmt='%H:%M:%S'))

    # try:
    main()
