#!/usr/bin/with-contenv bashio
set -euo pipefail

CAR_ID="$(bashio::config 'car_id')"

if [[ "${CAR_ID}" == "SOME_CAR_ID_HASH_CHANGE_ME" ]] || [[ -z "${CAR_ID}" ]]; then
  bashio::log.fatal "Option 'car_id' is required and must be changed from default value."
  exit 1
fi

export LISTEN=0.0.0.0
export PORT=12321
export CAR_ID
export API_KEY="$(bashio::config 'api_key')"
export API_KEY_RW="$(bashio::config 'api_key_rw')"
export TIMEOUT="$(bashio::config 'timeout')"
export REFRESH_INTERVAL="$(bashio::config 'refresh_interval')"
export SENSORS_REFRESH_INTERVAL="$(bashio::config 'sensors_refresh_interval')"
export JSON_SUB="$(bashio::config 'json_sub')"
export DEBUG="$(bashio::config 'debug')"

export EVOLUTE_TOKEN_FILENAME=/config/evy-platform-access.txt
export EVOLUTE_REFRESH_TOKEN_FILENAME=/config/evy-platform-refresh.txt

exec python3 /opt/evolute_api.py
