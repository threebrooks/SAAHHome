#!/bin/bash -e

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf

SAAH_INSTALL=~/SAAH/install
export PYTHONPATH=$SAAH_INSTALL
. $SAAH_INSTALL/Godec/env.sh
. $SAAH_INSTALL/env.sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/boost_1_74_0/stage/lib

python3 run.py
