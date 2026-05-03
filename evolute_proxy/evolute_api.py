import os
import json
import time
import logging
import threading
import sys
import re
import requests
from flask import Flask, request, jsonify, abort
from datetime import datetime
from flask import Response
from urllib.parse import urljoin


LISTEN = os.getenv("LISTEN", "127.0.0.1")
PORT = int(os.getenv("PORT", 12321))
API_KEY = os.getenv("API_KEY", "change_me")
API_KEY_RW = os.getenv("API_KEY_RW", "change_me_rw")
TIMEOUT = int(os.getenv("TIMEOUT", 60))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 600))
SENSORS_REFRESH_INTERVAL = int(os.getenv("SENSORS_REFRESH_INTERVAL", 120))
CAR_INFO_REFRESH_INTERVAL = int(os.getenv("CAR_INFO_REFRESH_INTERVAL", 3600))
JSON_SUB = os.getenv("JSON_SUB", ".sensors")
EVOLUTE_TOKEN_FILENAME = os.getenv("EVOLUTE_TOKEN_FILENAME", "evy-platform-access.txt")
EVOLUTE_REFRESH_TOKEN_FILENAME = os.getenv("EVOLUTE_REFRESH_TOKEN_FILENAME", "evy-platform-refresh.txt")
CAR_ID = os.getenv("CAR_ID", "SOME_CAR_ID_HASH_CHANGE_ME")

current_refresh_interval = REFRESH_INTERVAL

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36"
)

DUMP_FILE = os.getenv("DUMP_FILE", "/data/dump.json")
STATUS_FILE = os.getenv("STATUS_FILE", "/data/status.json")

EVOLUTE_REFRESH_URL = "https://app.evassist.ru/id-service/auth/refresh-token"
EVOLUTE_SENSOR_URL = f"https://app.evassist.ru/car-service/tbox/{CAR_ID}/info"
EVOLUTE_CAR_INFO_URL = f"https://app.evassist.ru/car-service/car/v2/{CAR_ID}"

INTELLIGENT_ACTIONS = {
    "lock_close": ("centralLockingToggle", "centralLockingStatus", 1),
    "lock_open": ("centralLockingToggle", "centralLockingStatus", 0),
    "heating_off": ("heating", "climateStatus", 0),
    "heating_on": ("heating", "climateStatus", 1),
    "cooling_off": ("cooling", "climateStatus", 0),
    "cooling_on": ("cooling", "climateStatus", 1),
    "trunk_close": ("trunkOpen", "trunkStatus", 0),
    "trunk_open": ("trunkOpen", "trunkStatus", 1),
    "prepare_on": ("PREPARE", "ignitionStatus", 1),
    "prepare_off": ("CANCEL", "ignitionStatus", 0),
    "blink": ("blink", "ready", 1),
}


LOG_LEVEL = logging.DEBUG if os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on") else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(levelname)s] %(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

sensors_data = {}
latest_sensors_root = {}
latest_sensors_meta = {}
latest_sensors_full = {}
latest_car_info = {}
status_info = {
    "start_time": datetime.utcnow().isoformat(),
    "last_token_update": None,
    "last_sensor_update": None,
}
tokens_ok = False
start_timestamp = time.time()


def _decode_body(data):
    if data is None:
        return ""
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return str(data)


def _sanitize_headers(headers):
    sanitized = dict(headers)
    for key in list(sanitized.keys()):
        if key.lower() == "x-api-key":
            sanitized[key] = "***"
    return sanitized


def _sanitize_svg_icons(value):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key in ("light", "dark") and isinstance(item, str) and item.lstrip().startswith("<svg"):
                sanitized[key] = "<svg omitted>"
            else:
                sanitized[key] = _sanitize_svg_icons(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_svg_icons(item) for item in value]
    return value


def _sanitize_logged_body(body):
    try:
        payload = json.loads(body)
        sanitized_payload = _sanitize_svg_icons(payload)
        return json.dumps(sanitized_payload, ensure_ascii=False)
    except Exception:
        return re.sub(r"<svg[^>]*>.*?</svg>", "<svg omitted>", body, flags=re.DOTALL)


def log_evolute_response(context, response):
    body = _sanitize_logged_body(_decode_body(response.content))
    logger.info(
        "Evolute response [%s]: status=%s headers=%s body=%s",
        context,
        response.status_code,
        dict(response.headers),
        body,
    )

def read_json_file(filename, default=None):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return default or {}

def write_json_file(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write {filename}: {e}")

def load_token(filename):
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_token(filename, token):
    with open(filename, "w") as f:
        f.write(token.strip())

def get_tokens():
    return {
        "access": load_token(EVOLUTE_TOKEN_FILENAME),
        "refresh": load_token(EVOLUTE_REFRESH_TOKEN_FILENAME),
    }

def update_status(key):
    status_info[key] = datetime.utcnow().isoformat()
    write_json_file(STATUS_FILE, status_info)

def refresh_tokens():
    global tokens_ok, current_refresh_interval
    try:
        tokens = get_tokens()
        payload = {"refreshToken": tokens["refresh"]}
        response = requests.post(EVOLUTE_REFRESH_URL, json=payload, timeout=TIMEOUT)
        log_evolute_response("token_refresh", response)
        response.raise_for_status()

        data = response.json()
        save_token(EVOLUTE_TOKEN_FILENAME, data["accessToken"])
        save_token(EVOLUTE_REFRESH_TOKEN_FILENAME, data["refreshToken"])
        update_status("last_token_update")
        tokens_ok = True

        if current_refresh_interval != REFRESH_INTERVAL:
            logger.info(f"Token refresh successful. Resetting interval to {REFRESH_INTERVAL}s")
            current_refresh_interval = REFRESH_INTERVAL
        else:
            logger.info("Tokens refreshed successfully")

    except requests.exceptions.HTTPError as e:
        tokens_ok = False
        if e.response is not None and e.response.status_code == 403:
            new_interval = min(current_refresh_interval * 2, 3600)
            logger.warning(f"403 Forbidden during token refresh. Increasing cooldown from {current_refresh_interval}s to {new_interval}s")
            current_refresh_interval = new_interval
        else:
            logger.error(f"HTTP error refreshing tokens: {e}")

    except Exception as e:
        tokens_ok = False
        logger.error(f"Failed to refresh tokens: {e}")

def fetch_sensor_data():
    global sensors_data, latest_sensors_root, latest_sensors_meta, latest_sensors_full
    if not tokens_ok:
        logger.warning("Sensor data fetch skipped: tokens are not active")
        return
    try:
        tokens = get_tokens()
        cookies = {
            "evy-platform-access": tokens["access"],
            "evy-platform-refresh": tokens["refresh"]
        }
        headers = {
            "User-Agent": USER_AGENT
        }
        response = requests.get(EVOLUTE_SENSOR_URL, headers=headers, cookies=cookies, timeout=TIMEOUT)
        log_evolute_response("sensor_fetch", response)
        response.raise_for_status()
        full_payload = response.json()
        latest_sensors_full = full_payload if isinstance(full_payload, dict) else {}
        latest_sensors_root = full_payload.get("sensors", {}) if isinstance(full_payload, dict) else {}

        # Keep scalar metadata from both likely roots because Evolute may place
        # fields like `isOnline` either in `sensors` or in the top-level payload.
        latest_sensors_meta = {}
        if isinstance(full_payload, dict):
            for root in (full_payload, latest_sensors_root):
                if not isinstance(root, dict):
                    continue
                for key, value in root.items():
                    if key in ("sensorsData", "positionData") or isinstance(value, (dict, list)):
                        continue
                    latest_sensors_meta[key] = value

        data = full_payload
        keys = JSON_SUB.strip(".").split(".")
        for k in keys:
            data = data.get(k, {})
        sensors_data = data
        update_status("last_sensor_update")
        write_json_file(DUMP_FILE, sensors_data)
        logger.info("Sensor data updated")
    except Exception as e:
        logger.error(f"Failed to fetch sensor data: {e}")



def fetch_car_info_data():
    global latest_car_info
    if not tokens_ok:
        logger.warning("Car info data fetch skipped: tokens are not active")
        return
    try:
        tokens = get_tokens()
        cookies = {
            "evy-platform-access": tokens["access"],
            "evy-platform-refresh": tokens["refresh"]
        }
        headers = {
            "User-Agent": USER_AGENT
        }
        response = requests.get(EVOLUTE_CAR_INFO_URL, headers=headers, cookies=cookies, timeout=TIMEOUT)
        log_evolute_response("car_info_fetch", response)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            logger.warning("Car info payload is not a JSON object")
            return

        car_model = payload.get("carModel") if isinstance(payload.get("carModel"), dict) else {}
        latest_car_info = {
            "vin": payload.get("vin"),
            "carModelName": car_model.get("name"),
            "carModelModname": car_model.get("modname"),
            "carModelYear": car_model.get("modelYear"),
            "carModelColor": car_model.get("color"),
        }
        logger.info("Car info data updated")
    except Exception as e:
        logger.error(f"Failed to fetch car info data: {e}")

def periodic_refresh():
    refresh_tokens()
    t = threading.Timer(current_refresh_interval, periodic_refresh)
    t.daemon = True
    t.start()

def periodic_fetch():
    fetch_sensor_data()
    t = threading.Timer(SENSORS_REFRESH_INTERVAL, periodic_fetch)
    t.daemon = True
    t.start()

def periodic_car_info_fetch():
    fetch_car_info_data()
    t = threading.Timer(CAR_INFO_REFRESH_INTERVAL, periodic_car_info_fetch)
    t.daemon = True
    t.start()

def check_auth(req):
    key = req.headers.get("X-API-Key") or req.args.get("api_key")
    if key != API_KEY:
        abort(jsonify({"error": "Unauthorized"}), 401)

def check_auth_rw(req):
    key = req.headers.get("X-API-Key") or req.args.get("api_key")
    if key != API_KEY_RW:
        abort(jsonify({"error": "Unauthorized"}), 401)


@app.before_request
def log_home_assistant_request():
    logger.info(
        "Home Assistant request: method=%s path=%s query=%s headers=%s body=%s",
        request.method,
        request.path,
        dict(request.args),
        _sanitize_headers(request.headers),
        _decode_body(request.get_data()),
    )


@app.after_request
def log_home_assistant_response(response):
    response_body = _sanitize_logged_body(_decode_body(response.get_data()))
    logger.info(
        "Home Assistant response: method=%s path=%s status=%s headers=%s body=%s",
        request.method,
        request.path,
        response.status_code,
        dict(response.headers),
        response_body,
    )
    return response

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200

@app.route("/status", methods=["GET"])
def status():
    uptime_seconds = time.time() - start_timestamp
    return jsonify({
        "alive": True,
        "uptime": uptime_seconds,
        "start_time": status_info["start_time"],
        "last_token_update": status_info["last_token_update"],
        "last_sensor_update": status_info["last_sensor_update"],
        "tokens_active": tokens_ok,
        "current_refresh_interval": current_refresh_interval
    })

@app.route("/set_tokens", methods=["POST"])
def set_tokens():
    global current_refresh_interval
    check_auth(request)
    data = request.get_json(force=True)
    access = data.get("access")
    refresh = data.get("refresh")
    if access:
        save_token(EVOLUTE_TOKEN_FILENAME, access)
    if refresh:
        save_token(EVOLUTE_REFRESH_TOKEN_FILENAME, refresh)

    current_refresh_interval = REFRESH_INTERVAL

    return jsonify({"status": "tokens updated"})

@app.route("/manual_refresh", methods=["POST"])
def manual_refresh():
    check_auth(request)
    refresh_tokens()
    return jsonify({"status": "refreshed", "interval": current_refresh_interval})

@app.route("/sensors/all", methods=["GET"])
def get_all_sensors():
    check_auth(request)

    # JSON_SUB may point either to `.sensors` (root) or directly to
    # `.sensors.sensorsData` (flat payload). Support both shapes.
    if isinstance(sensors_data, dict) and isinstance(sensors_data.get("sensorsData"), dict):
        sensors = sensors_data.get("sensorsData")
    elif isinstance(sensors_data, dict):
        sensors = sensors_data
    else:
        sensors = None

    if not sensors:
        return jsonify({"error": "No sensors data available"}), 404

    response_payload = dict(sensors)

    def _merge_scalar_root_fields(root):
        if not isinstance(root, dict):
            return
        for key, value in root.items():
            if key in ("sensorsData", "positionData"):
                continue
            if isinstance(value, (dict, list)):
                continue
            response_payload[key] = value

    # Merge scalar metadata from both cached root payload variants.
    _merge_scalar_root_fields(sensors_data)
    _merge_scalar_root_fields(latest_sensors_root)
    _merge_scalar_root_fields(latest_sensors_meta)

    def _merge_preparation_script_status(root):
        if not isinstance(root, dict):
            return
        preparation_script = root.get("preparation_script")
        if not isinstance(preparation_script, dict):
            return
        running = preparation_script.get("running")
        available = preparation_script.get("available")
        disabled = preparation_script.get("disabled")
        end_time = preparation_script.get("endTime")
        start_time = preparation_script.get("startTime")
        if isinstance(running, bool):
            response_payload["preparation_scriptIsrunning"] = running
        if isinstance(available, bool):
            response_payload["preparation_scriptAvailable"] = available
        if isinstance(disabled, bool):
            response_payload["preparation_scriptDisabled"] = disabled
        if end_time is not None:
            response_payload["preparation_scriptEndTime"] = end_time
        if start_time is not None:
            response_payload["preparation_scriptStartTime"] = start_time

    _merge_preparation_script_status(sensors_data)
    _merge_preparation_script_status(latest_sensors_full)
    _merge_preparation_script_status(latest_sensors_root)
    _merge_preparation_script_status(latest_sensors_meta)

    for key, value in latest_car_info.items():
        if value is not None:
            response_payload[key] = value

    # Keep backward-compatible alias for Home Assistant templates.
    sensor_time = response_payload.get("time")
    if sensor_time is None and isinstance(sensors_data, dict):
        sensor_time = sensors_data.get("time")
    if sensor_time is None and isinstance(latest_sensors_root, dict):
        sensor_time = latest_sensors_root.get("time")
    if sensor_time is None and isinstance(latest_sensors_meta, dict):
        sensor_time = latest_sensors_meta.get("time")
    if sensor_time is not None and "sensorDataTime" not in response_payload:
        response_payload["sensorDataTime"] = sensor_time

    return jsonify(response_payload)

@app.route("/position/all", methods=["GET"])
def get_all_positions():
    check_auth(request)
    position = sensors_data.get("positionData")
    if position:
        return jsonify(position)
    else:
        return jsonify({"error": "No position data available"}), 404

@app.route("/sensors/<string:sensor_name>", methods=["GET"])
def get_single_sensor(sensor_name):
    check_auth_rw(request)
    value = sensors_data.get(sensor_name)
    if value is None:
        return jsonify({"error": "sensor not found"}), 404
    return jsonify({sensor_name: value})

@app.route("/proxy/<path:subpath>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def proxy(subpath):
    check_auth_rw(request)
    tokens = get_tokens()
    base_url = "https://app.evassist.ru/"
    target_url = urljoin(base_url, subpath)

    method = request.method
    headers = {
        "User-Agent": USER_AGENT
    }
    headers.update({
        k: v for k, v in request.headers.items()
        if k.lower() not in ["host", "content-length", "content-type", "x-api-key"]
    })

    if request.content_type:
        headers["Content-Type"] = request.content_type

    cookies = {
        "evy-platform-access": tokens["access"],
        "evy-platform-refresh": tokens["refresh"]
    }

    try:
        resp = requests.request(
            method,
            target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=cookies,
            timeout=TIMEOUT,
            allow_redirects=False
        )
        log_evolute_response(f"proxy/{subpath}", resp)
        excluded_headers = ["content-encoding", "transfer-encoding", "connection"]
        response_headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        return Response(resp.content, resp.status_code, response_headers)
    except Exception as e:
        logger.error(f"Proxy request failed: {e}")
        return jsonify({"error": "Proxy failed"}), 500

@app.route("/tbox/<string:action>", methods=["POST"])
def tbox_action(action):
    check_auth_rw(request)
    tokens = get_tokens()
    target_url = f"https://app.evassist.ru/car-service/tbox/{CAR_ID}/{action}"

    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json"
    }

    cookies = {
        "evy-platform-access": tokens["access"],
        "evy-platform-refresh": tokens["refresh"]
    }

    try:
        resp = requests.post(
            target_url,
            headers=headers,
            data=request.get_data(),
            cookies=cookies,
            timeout=TIMEOUT
        )
        log_evolute_response(f"tbox/{action}", resp)
        resp.raise_for_status()
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"TBox action request failed: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/tbox-i/<string:action>", methods=["POST"])
def tbox_i_action(action):
    check_auth_rw(request)

    if action not in INTELLIGENT_ACTIONS:
        return jsonify({"status": "error", "error": f"Unknown intelligent action: {action}"}), 400

    endpoint, status_key, skip_if_value = INTELLIGENT_ACTIONS[action]

    try:
        fetch_sensor_data()
        current_value = sensors_data.get("sensorsData", {}).get(status_key)

        if current_value == skip_if_value:
            logger.info(f"Intelligent action '{action}' skipped: already in desired state")
            return jsonify({"status": "already_ok"})

        target_url = f"https://app.evassist.ru/car-service/tbox/{CAR_ID}/{endpoint}"
        tokens = get_tokens()
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        }
        cookies = {
            "evy-platform-access": tokens["access"],
            "evy-platform-refresh": tokens["refresh"]
        }

        resp = requests.post(
            target_url,
            headers=headers,
            data=request.get_data(),
            cookies=cookies,
            timeout=TIMEOUT
        )
        log_evolute_response(f"tbox-i/{action}", resp)
        resp.raise_for_status()
        logger.info(f"Intelligent action '{action}' executed successfully")
        fetch_sensor_data()

        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(f"Intelligent action '{action}' failed: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method Not Allowed"}), 405

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled error: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    if CAR_ID == "SOME_CAR_ID_HASH_CHANGE_ME":
        logger.error("Critical environment variable CAR_ID is not set. Exiting.")
        sys.exit(1)

    start_timestamp = time.time()

    sensors_data = read_json_file(DUMP_FILE, default={})
    loaded_status = read_json_file(STATUS_FILE, default={})
    status_info.update({k: v for k, v in loaded_status.items() if k in status_info})

    periodic_refresh()
    periodic_fetch()
    periodic_car_info_fetch()

    logger.info("App started")
    app.run(host=LISTEN, port=PORT)
