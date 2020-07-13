docker build -t fetch_status .
docker run --rm -ti \
	-e "GENESIS_PATH=${GENESIS_PATH}" \
	-e "GENESIS_URL=${GENESIS_URL}" \
	-e "SEED=${SEED}" \
	-p 8000:8000 \
	fetch_status
