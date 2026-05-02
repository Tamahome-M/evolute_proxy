# Changelog

## 1.0.25

- Exposed vehicle status chip metadata in `/sensors/all` as `chipId` and `chipTitle`.
- Added Home Assistant text sensor `sensor.evolute_status_text` sourced from `chipTitle`.
- Bumped add-on version to `1.0.25`.

## 1.0.24

- Improved `/sensors/all` merging logic to preserve existing `sensorsData` keys while exposing top-level online/status fields.
- Hardened Home Assistant template for `binary_sensor.evolute_online` to better handle boolean/string variations.
- Bumped add-on version to `1.0.24`.

## 1.0.23

- Fixed sensor normalization so `/sensors/all` includes `isOnline`, `lastOnlineTime`, and `sensorDataTime` (mapped from top-level `time` when needed).
- Added Home Assistant compatibility alias sensor `Evolute Coolant Temp` for dashboards that expect `sensor.evolute_coolant_temp`.
- Bumped add-on version to `1.0.23`.

## 1.0.21

- Added add-on option `debug` to enable/disable verbose logging.
- Bumped add-on version to `1.0.21`.

## 1.0.0

- Initial Home Assistant add-on packaging.
- Tokens moved to add-on configuration options.
