# Evolute Proxy add-on

Прокси к API Evolute для Home Assistant.

## Установка

1. В Home Assistant откройте **Settings → Add-ons → Add-on Store**.
2. Нажмите меню (⋮) → **Repositories**.
3. Добавьте URL этого репозитория.
4. Откройте add-on **Evolute Proxy** и установите его.

## Настройка

- `car_id` (**обязательно**) — ID автомобиля.
- `api_key` — ключ для read-only API прокси.
- `api_key_rw` — ключ для write API (`/tbox`, `/proxy`).
- `access_token`, `refresh_token` — токены Evolute (из браузера).
- `timeout`, `refresh_interval`, `sensors_refresh_interval`, `json_sub` — тонкая настройка.

## Как обновлять токены

Теперь токены задаются через конфигурацию add-on (поля `access_token` и `refresh_token`) через UI Home Assistant.
После изменения конфигурации нажмите **Save** и **Restart** add-on.

## Эндпоинты

- `GET /ping`
- `GET /status`
- `POST /manual_refresh`
- `GET /sensors/all`
- `GET /position/all`
- `GET /sensors/<sensor_name>`
- `POST /tbox/<action>`
- `POST /tbox-i/<action>`
- `ANY /proxy/<path>`
