#!/bin/bash
##################################################
## Author: Andrea Marcelli                      ##
## Phd @ Politecnico di Torino                  ##
## andrea.marcelli@polito.it                    ##
## 27/09/2017 - Somewhere in Italy              ##
## CrowdSignals.io                              ##
##################################################

mkdir temp;
for n in {1..6}; do echo $n; mkdir temp/User$n; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Base/* -name "c-applications*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Base/* -name "c-battery*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Base/* -name "c-network_traffic*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Base/* -name "c-screen*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Base/* -name "c-step_counter*.json" -exec cp {} temp/User$n/ \;; done

for n in {1..6}; do echo $n; find ./JSON-User$n-Mobility/* -name "c-cell*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Mobility/* -name "c-connectivity*.json" -exec cp {} temp/User$n/ \;; done
for n in {1..6}; do echo $n; find ./JSON-User$n-Mobility/* -name "c-wlan*.json" -exec cp {} temp/User$n/ \;; done

for n in {1..6}; do echo $n; find ./JSON-User$n-Survey/* -name "s-Current\ Place-*.json" -exec cp {} temp/User$n/ \;; done
