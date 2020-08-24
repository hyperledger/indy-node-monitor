#!/bin/bash
# set -x

export MSYS_NO_PATHCONV=1

# Running on Windows?
if [[ "$OSTYPE" == "msys" ]]; then
  # Prefix interactive terminal commands ...
  terminalEmu="winpty"
fi

# IM is for "interactive mode" so Docker is run with the "-it" parameter. Probably never needed
# but it is there. Use "IM=1 run.sh <args>..." to run the Docker container in interactive mode
if [ -z "${IM+x}" ]; then
  export DOCKER_INTERACTIVE=""
else
  export DOCKER_INTERACTIVE="-it"
fi

docker build -t fetch_status . > /dev/null 2>&1
${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
    -e "GENESIS_PATH=${GENESIS_PATH}" \
    -e "GENESIS_URL=${GENESIS_URL}" \
    -e "SEED=${SEED}" \
    fetch_status "$@"
