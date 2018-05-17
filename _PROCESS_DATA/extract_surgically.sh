#!/bin/bash
##################################################
## Author: Andrea Marcelli                      ##
## Phd @ Politecnico di Torino                  ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

for n in {1..43};
do
  echo "user: $n"

  # Base
  tar -xzvf JSON-User$n-Base.tar.gz --wildcards --no-anchored "c-applications*"
  tar -xzvf JSON-User$n-Base.tar.gz --wildcards --no-anchored "c-battery*"
  tar -xzvf JSON-User$n-Base.tar.gz --wildcards --no-anchored "c-network_traffic*"
  tar -xzvf JSON-User$n-Base.tar.gz --wildcards --no-anchored "c-screen*"
  tar -xzvf JSON-User$n-Base.tar.gz --wildcards --no-anchored "c-step_counter*"

  # Mobility
  # tar -xzvf *Mobility.tar.gz --wildcards --no-anchored "c-cell*"
  # tar -xzvf *Mobility.tar.gz --wildcards --no-anchored "c-connectivity*"
  # tar -xzvf *Mobility.tar.gz --wildcards --no-anchored "c-wlan*"

  # Survey
  # tar -xzvf *Survey.tar.gz --wildcards --no-anchored "s-Current\ Place-*"
done
