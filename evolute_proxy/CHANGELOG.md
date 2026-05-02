# Changelog

## 1.0.37

- Fixed `/sensors/all` compatibility for nested `JSON_SUB` and explicit `isOnline`/`lastOnlineTime` fallback.
- Bumped add-on version to `1.0.37`.

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
