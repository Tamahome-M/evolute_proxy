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
