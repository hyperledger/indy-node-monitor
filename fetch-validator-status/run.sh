#!/bin/bash
export MSYS_NO_PATHCONV=1

# Running on Windows?
if [[ "$OSTYPE" == "msys" ]]; then
  # Prefix interactive terminal commands ...
  terminalEmu="winpty"
fi

docker build -t fetch_status . > /dev/null 2>&1
${terminalEmu} docker run --rm -ti \
    -e "GENESIS_PATH=${GENESIS_PATH}" \
    -e "GENESIS_URL=${GENESIS_URL}" \
    -e "SEED=${SEED}" \
    fetch_status "$@"