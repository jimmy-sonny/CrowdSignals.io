#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################
## Author: Andrea Marcelli                      ##
## Phd @ Politecnico di Torino                  ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

import logging
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import json
import os
from datetime import datetime

ALL_FIELDS = [ "c-applications",
                    "c-cell",
                    "c-wlan" ]

BASE = [ "c-applications",
        "c-battery",
        "c-network_traffic",
        "c-screen",
        "c-step_counter" ]
        # "c-accelerometer",
        # "c-pressure",
        # "c-proximity",
        # "c-rotation_vector",
        # "c-gravity",
        # "c-gyroscope",
        # "c-gyroscope_uncalibrated",
        # "c-light",
        # "c-linear_acceleration",
        # "c-magnetometer",
        # "c-sensor_metadata" ]

MOBILITY = ["c-cell",
            "c-connectivity",
            "c-wlan" ]

# LABEL_META = [ # "s-Bus",
                # "s-Drinking",
                # "s-Escalator",
                # "s-LightRail",
                # "s-Walking" ]

SURVEY = [ "s-Current Place" ]
            # "s-Mood and Wellbeing",
            # "s-Phone Position",
            # "s-Sedentary Activity" ]


# lambda expressions for date features engineering
date = lambda x: datetime.fromtimestamp(int(str(x)[:10])).strftime('%Y-%m-%d %H:%M:%S')
day_of_week = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).weekday()
month = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).month
day = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).day
hour = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).hour
minute = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).minute
second = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).second
# (12-05) sleep(0);; (06-08) breakfast(1);; (09-11) work(2);; (12-13) lunch(3);;
# (14-17) work_afternoon(4);; (18-19) evening_activities(5);; (20-21) dinner(6);; (21-23) night(7);
times_of_day = [0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 7, 7 ]
time_of_day = lambda x: times_of_day[datetime.strptime(x, "%Y-%m-%d %H:%M:%S").hour]


def add_data_features(output_file):
    ''' From timestamp to date features '''
    df = pd.read_csv(output_file, error_bad_lines=False, warn_bad_lines=False)
    try:
        column_name = 'pane_start'
        if 'pane_start' not in df.columns.tolist():
            column_name = 'timestamp'
        df['date'] = df[column_name].map(date)
        df['month'] = df['date'].map(month)
        df['day'] = df['date'].map(day)
        df['day_of_week'] = df['date'].map(day_of_week)
        df['hour'] = df['date'].map(hour)
        df['minute'] = df['date'].map(minute)
        df['second'] = df['date'].map(second)
        df['time_of_day'] = df['date'].map(time_of_day)
        # df.drop('date', axis=1, inplace=True)
        df.to_csv(output_file)
        logging.debug(df.shape)
    except:
        logging.warning("Skipping add data info")


def parse_file(path_to_file, f_out, first_row, all_fields=False):
    with open(path_to_file, encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)
            if first_row:
                for idx, key in enumerate(j.keys()):
                    if idx == len(j.keys())-1:
                        f_out.write(key)
                    else:
                        f_out.write(key+',')
                f_out.write('\n')
                first_row = False
            for idx, k in enumerate(j.keys()):
                val = str(j[k])
                if val.startswith('['):
                    if all_fields:
                        val = val[1:-1].replace(',',';')
                    else:
                        val= list(val[1:-1].split(','))[0]
                        #val = val.replace(',','')
                if idx == len(j.keys())-1:
                    f_out.write(val)
                else:
                    f_out.write(val+',')
            f_out.write('\n')
    return first_row


def scrape_data(input_folder, output_folder, types):
    for t_ in types:
        logging.debug("type: " + t_)
        if t_ in ALL_FIELDS:
            all_fields = True
        else:
            all_fields = False
        first_row = True
        output_file = os.path.join(output_folder, t_+'.csv')
        with open(output_file,'a+') as f_out:
            for j_file in os.listdir(input_folder):
                if j_file.startswith(t_):
                    first_row = parse_file(os.path.join(input_folder, j_file), f_out, first_row, all_fields)
        if first_row == True:
            logging.warning("Skipping.. no files found")
        else:
            add_data_features(output_file)


def scrape_data_simple(input_folder, output_file):
    first_row = True
    with open(output_file,'a+') as f_out:
        for j_file in os.listdir(input_folder):
            first_row = parse_file(os.path.join(input_folder, j_file), f_out, first_row)
    if first_row == True:
        logging.warning("Skipping.. no files found")
    else:
        add_data_features(output_file)


def main():
    # for user in ['1','6']:
    users = [1, 2, 6, 8, 9, 10, 11, 12, 16, 19, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 41, 43]
    for user in [str(_) for _ in list(users)]:
        logging.debug("Processing User: %s", user)

        logging.debug("Processing Base...")
        scrape_data("temp/User"+user, "csv/user"+user, BASE)

        logging.debug("Processing Mobility...")
        scrape_data("temp/User"+user, "csv/user"+user, MOBILITY)

        logging.debug("Processing labelMeta...")
        scrape_data_simple("temp/User"+user, "csv/user"+user+"/labelMeta.csv")

        logging.debug("Processing Survey...")
        scrape_data("temp/User"+user, "csv/user"+user, SURVEY)

        logging.debug(" ")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(message)s'))
    logging.warning(r'© Copyright Andrea Marcelli')
    logging.warning(r'')
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s.%(msecs)04d %(levelname)s:: %(message)s', datefmt='%H:%M:%S'))

    try:
        main()
    except Exception as e:
    	print('Oops! Something bad happened!')
    	print(str(e))
