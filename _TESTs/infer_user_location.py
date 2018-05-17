#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################
## Author: Andrea Marcelli                      ##
## Ph.D. @ Politecnico di Torino                ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

import argparse
import logging

import pandas as pd
import numpy as np
np.random.seed(42)

import os
import json
import time
import itertools

import hdbscan
from datetime import datetime
from collections import Counter

from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import homogeneity_completeness_v_measure

import coloredlogs
import logging
log = None


def get_data(df, n_components):
    data = df[df.columns[1:-1]].values
    data = data.astype(float, copy=False)
    log.debug("data shape: " + str(data.shape))
    log.debug(data)
    data_scaled = preprocessing.scale(data)
    if data_scaled.shape[1] <= n_components:
        log.debug("Skiiping scaling")
        data_scaled_reduced = data_scaled
    else:
        svd = TruncatedSVD(n_components=n_components)
        data_scaled_reduced = svd.fit_transform(data_scaled)
        log.debug("data_scaled_reduced shape: " +
                  str(data_scaled_reduced.shape))
    return data_scaled_reduced


def apply_hdbscan(data, min_cluster_size, min_samples):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size, min_samples=min_samples, memory='./chache')
    start = time.time()
    log.info("Fitting...")
    clusterer.fit(data)
    end = time.time()
    log.info('HDBSCAN finished in %f secondi', (end - start))
    n_classes = len(np.unique(clusterer.labels_))
    n_outliers = list(clusterer.labels_).count(-1)
    log.info("Found %d clusters (+1 outliers) and %d outliers",
             n_classes - 1, n_outliers)
    return clusterer.labels_, n_classes


def post_clustering(df):
    mcv_dict = dict()
    for x, y in df.groupby(['day', 'hour']):
        cc = Counter(y['HDBSCAN'].values)
        mcv_dict[x] = cc.most_common(1)[0][0]
    set2set = set()
    for x, y in df.groupby(['day', 'hour']):
        set2set.add(frozenset(y['HDBSCAN'].values))
    log.debug("clusters [hour] pattern size: %d", len(set2set))
    di = dict()
    it = 0
    for val in set2set:
        di[val] = it
        it += 1
    hourly_patterns = dict()
    for x, y in df.groupby(['day', 'hour']):
        hourly_patterns[x] = di[frozenset(y['HDBSCAN'].values)]
    return hourly_patterns, mcv_dict


def compare(hp_w, hp_c):
    kk = hp_w.keys() & hp_c.keys()
    log.debug("Found %d hours in common", len(kk))
    w = [hp_w[k] for k in kk]
    c = [hp_c[k] for k in kk]
    ari = adjusted_rand_score(w, c)
    h, c, v = homogeneity_completeness_v_measure(w, c)
    log.info("ARI: " + str(ari))
    log.info("H: %f, C: %f, V:%f", h, c, v)
    return ari, h, v, c


def main():
    ''' That's main! '''
    parser = argparse.ArgumentParser(
        description='[Unsupervised] Infer user location from CrowdSignals.io dataset')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='debug mode on')
    parser.add_argument('-c', '--cache', action='store_true',
                        help='use cached data')
    parser.add_argument('-u', '--user', type=int,
                        required=True, help='select to user to work on')
    parser.add_argument('-bf', '--bruteforce',
                        action='store_true', help='Brute forse comparison')

    args = parser.parse_args()

    global log
    log = logging.getLogger()
    loglevel = 'DEBUG'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s:: %(message)s',
                        datefmt='%H:%M:%S', level=loglevel, logger=log)

    log.info("Let's start!")

    if args.debug:
        log.getLogger().setLevel(level=log.DEBUG)

    cache = False
    if args.cache:
        cache = True

    user = args.user

    log.info("Reading Data Frame wireless...")
    df_w = pd.read_csv("csv/user" + str(user) +
                       "/df_wireless_processed.csv", index_col=0)
    if 'tenmins' in df_w.columns:
        del df_w['tenmins']
    if 'thirtymins' in df_w.columns:
        del df_w['thirtymins']

    log.info("Reading Data Frame cell...")
    df_c = pd.read_csv("csv/user" + str(user) +
                       "/df_cell_processed.csv", index_col=0)
    if 'tenmins' in df_c.columns:
        del df_c['tenmins']
    if 'thirtymins' in df_c.columns:
        del df_c['thirtymins']

    gg_w = df_w.groupby(['day', 'hour'])
    gg_c = df_c.groupby(['day', 'hour'])

    kw = df_w.groupby(['day', 'hour']).groups.keys()
    kc = df_c.groupby(['day', 'hour']).groups.keys()
    kk = kw & kc
    log.debug(len(kk))

    df_w = pd.concat([gg_w.get_group(k) for k in kk])
    log.debug(df_w.shape)
    df_c = pd.concat([gg_c.get_group(k) for k in kk])
    log.debug(df_c.shape)

    if cache:
        log.info("Loading data from cache...")
        data_w = np.load('csv/user' + str(user) + '/data_w.npy')
        data_c = np.load('csv/user' + str(user) + '/data_c.npy')
    else:
        log.info("Computing data with dimensionality reduction...")
        data_w = get_data(df_w, 50)
        data_c = get_data(df_c, 50)
        np.save('csv/user' + str(user) + '/data_w', data_w)
        np.save('csv/user' + str(user) + '/data_c', data_c)
        log.info("Data saved to cache for future usage...")

    if args.bruteforce:
        comparison = pd.DataFrame(columns=['mss_w', 'mss_c', 'ms_w', 'ms_c',
                                           'nc_wireless', 'nc_cell', 'ari1',
                                           'ari2', 'h1', 'h2', 'c1', 'c2',
                                           'v1', 'v2'])
        counter = 0
        mss = [10, 50, 100]
        ms = [10, 30, 50]
        for mss_w, mss_c, ms_w, ms_c in list(itertools.product(mss, mss, ms, ms)):
            log.info("%d %d %d %d", mss_w, mss_c, ms_w, ms_c)
            log.info("Clustering on wireless...")
            df_w['HDBSCAN'], n_wireless = apply_hdbscan(data_w, mss_w, ms_w)
            hp_w, mcv_w = post_clustering(df_w)
            log.info("Clustering on cell...")
            df_c['HDBSCAN'], n_cell = apply_hdbscan(data_c, mss_c, ms_c)
            hp_c, mcv_c = post_clustering(df_c)
            ari1, h1, v1, c1 = compare(hp_w, hp_c)
            ari2, h2, v2, c2 = compare(mcv_w, mcv_c)
            comparison.loc[counter] = [mss_w, mss_c, ms_w, ms_c, n_wireless,
                                       n_cell, ari1, ari2, h1, h2, c1, c2,
                                       v1, v2]
            counter += 1
        comparison.sort_values(by=['ari1']).to_csv(
            "csv/user" + str(user) + "/comparison_ari1.csv")
        comparison.sort_values(by=['ari2']).to_csv(
            "csv/user" + str(user) + "/comparison_ari2.csv")

    else:
        log.info("Clustering on wireless...")
        df_w['HDBSCAN'], _ = apply_hdbscan(data_w, 100, 10)
        hp_w, mcv_w = post_clustering(df_w)
        log.info("Clustering on cell...")
        df_c['HDBSCAN'], _ = apply_hdbscan(data_c, 10, 50)
        hp_c, mcv_c = post_clustering(df_c)
        compare(hp_w, hp_c)
        compare(mcv_w, mcv_c)

        temp = df_w[['timestamp', 'month', 'day', 'day_of_week',
                     'hour', 'minute', 'second', 'time_of_day', 'HDBSCAN']]
        temp.to_csv("csv/user" + str(user) + "/df_wireless_HDBSCAN.csv")

        temp = df_c[['timestamp', 'month', 'day', 'day_of_week',
                     'hour', 'minute', 'second', 'time_of_day', 'HDBSCAN']]
        temp.to_csv("csv/user" + str(user) + "/df_cell_HDBSCAN.csv")


if __name__ == '__main__':
    main()
