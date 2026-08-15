# QORJYN — Backend

Django 5.2 + DRF. Порт 4000.

Полная документация проекта: [README](../README.md), [API](../docs/API.md),
[архитектура](../docs/ARCHITECTURE.md), [разработка](../docs/DEVELOPMENT.md).

## Запуск

    python -m venv .venv
    .venv/Scripts/python -m pip install -r requirements.txt
    cp .env.example .env          # заполнить учетные данные Green API
    .venv/Scripts/python manage.py migrate
    .venv/Scripts/python manage.py seed_demo
    .venv/Scripts/python manage.py createsuperuser
    .venv/Scripts/python manage.py runserver 4000

## Тесты

    .venv/Scripts/python -m pytest -v

## WhatsApp

Отладка диалога без сети:

    .venv/Scripts/python manage.py bot_sim "Остатки"
    .venv/Scripts/python manage.py bot_sim "" --type image

Живой вебхук требует публичного адреса:

    ngrok http 4000

Затем в панели Green API указать `https://<ngrok>/api/webhook/greenapi`
и выставить `MOCK_GREEN_API=false` в `.env`.

## Админка

`http://localhost:4000/admin/` — справочники и журналы.
`http://localhost:4000/admin/analytics/` — аналитика использования.
