#!/usr/bin/with-contenv bashio
set -euo pipefail

CONFIG_PATH=/data/options.json

CAR_ID="$(bashio::config 'car_id')"
API_KEY="$(bashio::config 'api_key')"
API_KEY_RW="$(bashio::config 'api_key_rw')"
ACCESS_TOKEN="$(bashio::config 'access_token')"
REFRESH_TOKEN="$(bashio::config 'refresh_token')"
TIMEOUT="$(bashio::config 'timeout')"
REFRESH_INTERVAL="$(bashio::config 'refresh_interval')"
SENSORS_REFRESH_INTERVAL="$(bashio::config 'sensors_refresh_interval')"
JSON_SUB="$(bashio::config 'json_sub')"

if bashio::var.is_empty "${CAR_ID}"; then
  bashio::log.fatal "Option 'car_id' is required"
  exit 1
fi

printf '%s' "${ACCESS_TOKEN}" > /data/evy-platform-access.txt
printf '%s' "${REFRESH_TOKEN}" > /data/evy-platform-refresh.txt

export LISTEN="0.0.0.0"
export PORT="12321"
export CAR_ID
export API_KEY
export API_KEY_RW
export TIMEOUT
export REFRESH_INTERVAL
export SENSORS_REFRESH_INTERVAL
export JSON_SUB
export EVOLUTE_TOKEN_FILENAME="/data/evy-platform-access.txt"
export EVOLUTE_REFRESH_TOKEN_FILENAME="/data/evy-platform-refresh.txt"
export DUMP_FILE="/data/dump.json"
export STATUS_FILE="/data/status.json"

exec python3 /evolute_api.py
