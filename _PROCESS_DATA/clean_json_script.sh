#!/bin/bash
##################################################
## Author: Andrea Marcelli                      ##
## Phd @ Politecnico di Torino                  ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

array=(
  'c-accelerometer'
  'c-pressure'
  'c-proximity'
  'c-rotation_vector'
  'c-gravity'
  'c-gyroscope'
  'c-gyroscope_uncalibrated'
  'c-light'
  'c-linear_acceleration'
  'c-magnetometer'
  'c-sensor_metadata'
)

for n in "${array[@]}"; do echo $n; find . -name "$n*.json" -exec rm {} \;; done
