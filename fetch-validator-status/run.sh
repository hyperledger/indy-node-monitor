#!/bin/bash
# set -x

export MSYS_NO_PATHCONV=1

# --- Set program name here ---
program_name="fetch_status"

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

function isInstalled() {
  (
    if [ -x "$(command -v ${@})" ]; then
      return 0
    else
      return 1
    fi
  )
}

function echoYellow (){
  (
  _msg=${1}
  _yellow='\e[33m'
  _nc='\e[0m' # No Color
  echo -e "${_yellow}${_msg}${_nc}" >&2
  )
}

JQ_EXE=jq
if ! isInstalled ${JQ_EXE}; then
  echoYellow "The ${JQ_EXE} executable is required and was not found on your path."

  cat <<-EOF
  The recommended approach to installing the required package(s) is to use either [Homebrew](https://brew.sh/) (MAC)
  or [Chocolatey](https://chocolatey.org/) (Windows).  For more information visit https://stedolan.github.io/jq/

  Windows:
    - chocolatey install ${JQ_EXE}
  MAC:
    - brew install ${JQ_EXE}
  Debian/Ubuntu:
    - sudo apt-get install ${JQ_EXE}
EOF
  exit 1
fi

# fetch_status can have long running commands.
# Detect any existing containers running the same command and exit.
runningContainers=$(docker ps | grep ${program_name} | awk '{print $1}')
if [ ! -z "${runningContainers}" ]; then
  for runningContainer in ${runningContainers}; do
    runningContainerCmd=$(docker inspect ${runningContainer} | ${JQ_EXE} -r '.[0]["Config"]["Cmd"][0]')
    if [[ "${runningContainerCmd}" == "${@}" ]]; then 
      echoYellow "There is an instance of $program_name already running the same command.  Please wait for it to complete ..."
      exit 0
    fi
  done
fi

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

if [[ "$@" == *"--web"* ]]; then
  export DOCKER_PUBLISH="--publish 8080:8080"
else
  export DOCKER_PUBLISH=""
fi

docker build -t $program_name . > /dev/null 2>&1

cmd="${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
  -e "GENESIS_PATH=${GENESIS_PATH}" \
  -e "GENESIS_URL=${GENESIS_URL}" \
  -e "SEED=${SEED}" \
  ${DOCKER_PUBLISH}"

# Dynamically mount teh 'conf' directory if it exists.
if [ -d "./conf" ]; then
  cmd+=$(getVolumeMount "./conf")
fi

if [ -d "./plugins" ]; then
  cmd+=$(getVolumeMount "./plugins")
fi

cmd+="$program_name \"$@\""

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