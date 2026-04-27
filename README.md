# Evolute Proxy — Home Assistant Add-on Repository

Этот репозиторий подготовлен как **полноценный custom add-on repository** для Home Assistant.

## Что внутри

- `repository.yaml` — метаданные репозитория add-ons.
- `evolute_proxy/` — сам add-on (`config.yaml`, `Dockerfile`, `run.sh`, `DOCS.md`).
- `evolute_api.py` — Flask-прокси, запускаемый add-on.

## Установка через интерфейс Home Assistant

1. Откройте **Settings → Add-ons → Add-on Store**.
2. Нажмите меню (⋮) → **Repositories**.
3. Вставьте URL этого Git-репозитория и сохраните.
4. Найдите add-on **Evolute Proxy**, установите и запустите.

## Настройка токенов

Токены теперь задаются **через конфигурацию add-on** (UI Home Assistant):

- `access_token`
- `refresh_token`

После изменения конфигурации нажмите **Save** и **Restart**.

> `set_token.sh` оставлен только как legacy-утилита и для add-on больше не требуется.

## Команды управления TBox из Home Assistant

В папке `home-assistant/` добавлены готовые конфиги для intelligent API эндпоинта `POST /tbox-i/<action_name>`:

- `home-assistant/evolute_commands.yaml` — `rest_command` для всех поддерживаемых действий.
- `home-assistant/evolute_scripts.yaml` — `script`-обертки, чтобы запускать действия из UI/автоматизаций.
- `home-assistant/configuration.yaml` — пример подключения с отдельным `input_text.evolute_proxy_token_rw`.

Поддерживаемые `action_name`: `lock_open`, `lock_close`, `heating_on`, `heating_off`, `cooling_on`, `cooling_off`, `blink`, `trunk_open`, `trunk_close`, `prepare_on`, `prepare_off`.
