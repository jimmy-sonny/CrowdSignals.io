#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################
## Author: Andrea Marcelli                      ##
## Ph.D. @ Politecnico di Torino                ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

import sys
import os
import re

from collections import Counter
import matplotlib.pyplot as plt

import networkx as nx
import numpy as np
import pandas as pd
import pykov

import coloredlogs
import logging

path = 'csv/'
log = None


def main():
    global log
    log = logging.getLogger()
    loglevel = 'DEBUG'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s:: %(message)s',
                        datefmt='%H:%M:%S', level=loglevel, logger=log)

    log.debug("Let's start!")

    for _, dirs, _ in os.walk(path):
        for directory in sorted(dirs):
            if re.match('user[\d]+', directory):
                try:
                    print(" ")
                    log.info("Processing: %s", directory)

                    log.info("Reading Data Frame wireless...")
                    df_w = pd.read_csv(
                        path + os.path.join(directory, "df_wireless_HDBSCAN.csv"), index_col=0)

                    log.info("Reading Data Frame cellular...")
                    df_c = pd.read_csv(
                        path + os.path.join(directory, "df_cell_HDBSCAN.csv"), index_col=0)

                    kkw = set([k for k, _ in df_w.groupby(['day', 'hour'])])
                    log.debug("wireless key set len: %d", len(kkw))
                    kkc = set([k for k, _ in df_c.groupby(['day', 'hour'])])
                    log.debug("cell key set len: %d", len(kkc))
                    kk = kkc & kkw
                    log.debug("common key set len: %d", len(kk))

                    mcv_w_list = list()
                    mcv_c_list = list()

                    for k in sorted(kk):
                        _w = Counter(df_w.groupby(['day', 'hour']).get_group(k)[
                                     'HDBSCAN'].values)
                        mcv_w_list.append(_w.most_common(1)[0][0])

                        _c = Counter(df_c.groupby(['day', 'hour']).get_group(k)[
                                     'HDBSCAN'].values)
                        mcv_c_list.append(_c.most_common(1)[0][0])

                    mapping_w = {i: c for c, i in enumerate(
                        sorted(list(set(mcv_w_list))))}
                    log.debug(mapping_w)

                    mapping_c = {i: c for c, i in enumerate(
                        sorted(list(set(mcv_c_list))))}
                    log.debug(mapping_c)

                    hours = list()
                    for c, k in enumerate(sorted(kk)):
                        hours.append(k[2])

                    n = len(set(mcv_w_list))
                    mat_w = np.zeros([n, n])

                    c1 = 0
                    c2 = 0
                    for d, h in zip(list(zip(mcv_w_list[:-1], mcv_w_list[1:])), list(zip(hours[:-1], (hours[1:])))):
                        c1 += 1
                        if (h[1] == (h[0] + 1)) or ((h[1] == 0) and (h[0] == 23)):
                            c2 += 1
                            mat_w[mapping_w[d[0]]][mapping_w[d[1]]] += 1
                    markov_w = mat_w / mat_w.sum(axis=1)[:, np.newaxis]
                    markov_w = np.nan_to_num(markov_w)
                    markov_w = np.around(markov_w, decimals=2)

                    log.warning("Inserted %d/%d", c2, c1)

                    n = len(set(mcv_c_list))
                    mat_c = np.zeros([n, n])

                    c1 = 0
                    c2 = 0
                    for d, h in zip(list(zip(mcv_c_list[:-1], mcv_c_list[1:])), list(zip(hours[:-1], (hours[1:])))):
                        c1 += 1
                        if (h[1] == (h[0] + 1)) or ((h[1] == 0) and (h[0] == 23)):
                            c2 += 1
                            mat_c[mapping_c[d[0]]][mapping_c[d[1]]] += 1
                    markov_c = mat_c / mat_c.sum(axis=1)[:, np.newaxis]
                    markov_c = np.nan_to_num(markov_c)
                    markov_c = np.around(markov_c, decimals=2)

                    log.warning("Inserted %d/%d", c2, c1)

                    plt.imshow(markov_w, cmap='Blues', interpolation='nearest')
                    plt.xlabel('Meaningful locations')
                    plt.ylabel('Meaningful locations')
                    plt.savefig(path + os.path.join(directory,
                                                    "_markov_wireless.png"), dpi=300)

                    plt.imshow(markov_c, cmap='Blues', interpolation='nearest')
                    plt.xlabel('Meaningful locations')
                    plt.ylabel('Meaningful locations')
                    plt.savefig(path + os.path.join(directory,
                                                    "_markov_cell.png"), dpi=300)

                    with open(path + os.path.join(directory, "mat_w.markov"), 'w') as f_w:
                        for i in range(mat_w.shape[0]):
                            for j in range(mat_w.shape[1]):
                                f_w.writelines("%d %d %d\n" %
                                               (i, j, mat_w[i, j]))

                    with open(path + os.path.join(directory, "mat_c.markov"), 'w') as f_w:
                        for i in range(mat_c.shape[0]):
                            for j in range(mat_c.shape[1]):
                                f_w.writelines("%d %d %d\n" %
                                               (i, j, mat_c[i, j]))

                    P_c = pykov.readmat(
                        path + os.path.join(directory, "mat_c.markov"))
                    P_w = pykov.readmat(
                        path + os.path.join(directory, "mat_c.markov"))

                    try:
                        P_c.stochastic()
                        P_w.stochastic()
                    except pykov.PykovError:
                        log.critical("Cannot get a right stochastic matrix")

                except Exception:
                    log.exception("Skipping %s", directory)

    log.debug("Finished!")


if __name__ == '__main__':
    main()
