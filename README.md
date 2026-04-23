# Evolute API proxy + Home Assistant Add-on

Репозиторий содержит:

1. Прокси к облаку Evolute (`evolute_api.py`) для кэша сенсоров/позиции и безопасного проксирования API.
2. Полноценный Home Assistant Add-on (папка `addon/evolute_proxy`).
3. Структуру add-on репозитория Home Assistant (`repository.yaml` в корне), чтобы этот Git-репозиторий можно было добавить в HA как внешний репозиторий аддонов.

## Что умеет прокси

- Обновляет access/refresh токены.
- Кэширует сенсоры и позицию.
- Отдает REST-эндпоинты (`/sensors/all`, `/position/all`, `/status`, ...).
- Выполняет команды TBOX (`/tbox/*`, `/tbox-i/*`).

## Установка как Home Assistant Add-on

### 1) Добавить репозиторий в Home Assistant

В Home Assistant:

- **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
- Добавьте URL вашего форка/репозитория, например:

```text
https://github.com/Tamahome-M/evolute_proxy
```

### 2) Установить аддон `Evolute Proxy`

После добавления репозитория аддон появится в списке.

### 3) Настроить опции аддона

Обязательные:

- `car_id` — ID вашего авто
- `api_key` — ключ для read-запросов к прокси
- `api_key_rw` — ключ для команд (RW)

Опциональные:

- `timeout` (по умолчанию `60`)
- `refresh_interval` (по умолчанию `600`)
- `sensors_refresh_interval` (по умолчанию `120`)
- `json_sub` (по умолчанию `.sensors`)
- `debug` (по умолчанию `false`, включает подробные DEBUG-логи в аддоне)

### 4) Запустить аддон

Аддон слушает порт `12321/tcp`.

### 5) Передать токены (один раз или при необходимости)

Используйте `set_token.sh` (отредактируйте IP/ключ/токены) или вручную:

```bash
curl -X POST "http://<HA_IP>:12321/set_tokens" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api_key>" \
  -d '{"access":"<access_token>","refresh":"<refresh_token>"}'

curl -X POST "http://<HA_IP>:12321/manual_refresh" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api_key>"
```

## Структура Home Assistant Add-on

- `repository.yaml` — маркер репозитория аддонов для Home Assistant.
- `addon/evolute_proxy/config.yaml` — метаданные/настройки аддона.
- `addon/evolute_proxy/build.yaml` — базовые образы для разных архитектур.
- `addon/evolute_proxy/Dockerfile` — сборка контейнера аддона.
- `addon/evolute_proxy/run.sh` — запуск с чтением HA options через `bashio`.

## Локальный запуск без Home Assistant (как раньше)

Оставлен старый вариант запуска:

- `docker-compose.yml`
- `Dockerfile`
- `run.sh`

## Примеры для Home Assistant (сенсоры)

Примеры yaml лежат в папке `home-assistant/`.
