# Changelog

## 1.0.40

- Added periodic car metadata fetch from `car-service/car/v2/{CAR_ID}` and exposed VIN/model fields in `/sensors/all`.
- Added Home Assistant sensors/card entries for VIN, model, modname, year, and color.
- Bumped add-on version to `1.0.40`.

## 1.0.39

- Fixed `/sensors/all` to preserve scalar metadata from both top-level and `sensors` roots of Evolute response (including `isOnline`).
- Bumped add-on version to `1.0.39`.

## 1.0.38

- Fixed `/sensors/all` payload normalization so top-level metadata like `isOnline` is preserved with either JSON_SUB shape.
- Bumped add-on version to `1.0.38`.

## 1.0.36

- Bumped add-on version to `1.0.36`.

## 1.0.35

- Added `time` attribute to `home-assistant/evolute_rest.yaml` for users who reference the raw top-level timestamp directly.
- `/sensors/all` already exposes both `time` and backward-compatible `sensorDataTime`.
- Bumped add-on version to `1.0.35`.

## 1.0.34

- Updated `/sensors/all` to include all scalar top-level fields from Evolute payload in addition to `sensorsData`, preventing sensor attribute loss in Home Assistant.
- Kept backward-compatible `sensorDataTime` alias mapped from top-level `time`.
- Bumped add-on version to `1.0.34`.

## 1.0.33

- Fixed `/sensors/all` payload to include online state fields (`isOnline`, `lastOnlineTime`, `sensorDataTime`) for Home Assistant binary sensors.
- Bumped add-on version to `1.0.33`.

## 1.0.21

- Added add-on option `debug` to enable/disable verbose logging.
- Bumped add-on version to `1.0.21`.

## 1.0.0

- Initial Home Assistant add-on packaging.
- Tokens moved to add-on configuration options.
