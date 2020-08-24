#!/bin/bash
set -x

export MSYS_NO_PATHCONV=1

# Running on Windows?
if [[ "$OSTYPE" == "msys" ]]; then
  # Prefix interactive terminal commands ...
  terminalEmu="winpty"
fi

# CM is for "cron mode" so Docker is run the right way for cron
# Use "CM=1 run.sh <args>..." to run from a fron job to run Docker in non-interactive mode
if [ -z "${CM+x}" ]; then
  export DOCKER_INTERACTIVE="-it"
else
  export DOCKER_INTERACTIVE=""
fi

docker build -t fetch_status . > /dev/null 2>&1
${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
    -e "GENESIS_PATH=${GENESIS_PATH}" \
    -e "GENESIS_URL=${GENESIS_URL}" \
    -e "SEED=${SEED}" \
    fetch_status "$@"
