#!/usr/bin/env bash

# Copyright 2023 The DAPHNE Consortium
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARCH=X86-64

#on some installations docker can only be run with sudo
USE_SUDO=sudo
#USE_SUDO=

# run this script from the base path of your DAPHNE source tree
DAPHNE_ROOT=$PWD

# user info to set up your user inside the container (to avoid creating files that then belong to the root user)
USERNAME=$(id -n -u)
GID=$(id -g)

# some environment setup
CUDA_PATH=/usr/local/cuda
# temporarily adding this NSight Systems path
PATH=/opt/nvidia/nsight-compute/2023.2.2/host/target-linux-x64:$CUDA_PATH/bin:$DAPHNE_ROOT/bin:$PATH

# set bash as the default command if none is provided
# /app/daphne-X86-64-v0.2-bin/bin/daphne 
command=$*
if [ "$#" -eq 0 ]; then
    command=bash
fi


$USE_SUDO docker run  -it --hostname daphne-container \
    -e GID=$GID -e TERM=screen-256color -e PATH --gpus all \
    -e USER=$USERNAME -e UID=$UID \
    -v /home/philipp.hildebrandt/daphnelib_umlaut_example:/app/daphnelib_umlaut_example \
    -v /home/philipp.hildebrandt/End-to-end-ML-System-Benchmark:/app/new_umlaut \
    -v /home/philipp.hildebrandt/kai_material-degradation-master:/app/kai_material-degradation-master \
    --entrypoint /bin/bash "umlaut" 
