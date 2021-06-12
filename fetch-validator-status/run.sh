#!/bin/bash
# set -x

export MSYS_NO_PATHCONV=1

function getVolumeMount() {
  path=${1}
  path=$(realpath ${path})
  path=${path%%+(/)}
  mountPoint=${path##*/}
  if [[ "$OSTYPE" == "msys" ]]; then
    # When running on Windows, you need to prefix the path with an extra '/'
    path="/${path}"
  fi
  echo "  --volume='${path}:/home/indy/${mountPoint}:Z' "
}

function runCmd() {
  _cmd=${1}
  if [ ! -z ${LOG} ]; then
    _cmd+=" > ${LOG%.*}_`date +\%Y-\%m-\%d_%H-%M-%S`.json"
  fi

  eval ${_cmd}
  # echo
  # echo ${_cmd}
}

# IM is for "interactive mode" so Docker is run with the "-it" parameter. Probably never needed
# but it is there. Use "IM=1 run.sh <args>..." to run the Docker container in interactive mode
if [ -z "${IM+x}" ]; then
  export DOCKER_INTERACTIVE=""
else
  export DOCKER_INTERACTIVE="-it"
  
  # Running interactively on Windows?
  if [[ "$OSTYPE" == "msys" ]]; then
    # Prefix interactive terminal commands ...
    export terminalEmu="winpty"
  fi
fi

docker build -t fetch_status . #> /dev/null 2>&1

cmd="${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
  -e "GENESIS_PATH=${GENESIS_PATH}" \
  -e "GENESIS_URL=${GENESIS_URL}" \
  -e "SEED=${SEED}" \
  --publish 8080:8080"

# Dynamically mount teh 'conf' directory if it exists.
if [ -d "./conf" ]; then
  cmd+=$(getVolumeMount "./conf")
fi

if [ -d "./plugins" ]; then
  cmd+=$(getVolumeMount "./plugins")
fi

cmd+="fetch_status \"$@\""

counter=${SAMPLES:-1}
while [[ ${counter} > 0 ]]
do
  runCmd "${cmd}"
  counter=$(( ${counter} - 1 ))
  if [[ ${counter} > 0 ]]; then
    # Nodes update their validator info every minute.
    # Therefore calling more than once per minute is not productive.
    sleep 60
  fi
done