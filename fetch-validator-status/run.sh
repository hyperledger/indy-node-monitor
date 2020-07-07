docker build -t fetch_status .
docker run --rm -ti \
	-e "GENESIS_PATH=${GENESIS_PATH}" \
	-e "GENESIS_URL=${GENESIS_URL}" \
	-e "SEED=${SEED}" \
	fetch_status
