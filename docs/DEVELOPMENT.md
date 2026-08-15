# Разработка и запуск

## Требования

- Python 3.11+;
- Node.js 20+ и npm;
- Git;
- PostgreSQL опционально;
- ngrok или другой tunnel только для живого Green API webhook.

## Backend

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 4000
```

### Linux/macOS

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 4000
```

## Frontend

```powershell
cd frontend
npm ci
Copy-Item .env.local.example .env.local
npm run dev
```

Frontend работает на <http://localhost:3000>, backend — на <http://localhost:4000>.

## Переменные backend

| Переменная | Назначение | Локальное значение |
|---|---|---|
| `DJANGO_SECRET_KEY` | Секрет Django | обязательно заменить вне dev |
| `DJANGO_DEBUG` | Режим debug | `true` |
| `ALLOWED_HOSTS` | Разрешенные host headers | `*` только локально |
| `DATABASE_URL` | Подключение к БД | пусто = SQLite |
| `GREEN_API_INSTANCE` | ID инстанса Green API | опционально в mock режиме |
| `GREEN_API_TOKEN` | Токен Green API | опционально в mock режиме |
| `MOCK_GREEN_API` | Не выполнять сетевую отправку | `true` |

Frontend использует `NEXT_PUBLIC_API_URL`, по умолчанию `http://localhost:4000/api`.

## Тесты и проверки

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate --check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
cd frontend
npm ci
npm run build
```

## Demo-данные

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py seed_demo
```

Команда безопасна для demo-окружения, но очищает и пересоздает доменные данные. Django users не удаляются.

## Django Admin

Создайте администратора:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Адреса:

- <http://localhost:4000/admin/>;
- <http://localhost:4000/admin/analytics/>.

Доменные журналы в Admin защищены от случайного удаления. Reset demo сохраняет учетную запись администратора.

## WhatsApp / Green API

### Локальная симуляция

При `MOCK_GREEN_API=true`:

```powershell
.\.venv\Scripts\python.exe manage.py bot_sim "Остатки"
.\.venv\Scripts\python.exe manage.py bot_sim "" --type image
```

Сообщения не уходят во внешнюю сеть, а выводятся в лог.

### Живой webhook

1. Заполните `GREEN_API_INSTANCE` и `GREEN_API_TOKEN`.
2. Установите `MOCK_GREEN_API=false`.
3. Опубликуйте порт 4000, например `ngrok http 4000`.
4. Укажите в Green API URL `https://<host>/api/webhook/greenapi`.

Никогда не коммитьте `.env` и реальные credentials.

## PostgreSQL

Передайте стандартный URL:

```text
DATABASE_URL=postgresql://user:password@host:5432/qorjyn
```

Затем выполните `manage.py migrate`. Сервисы, использующие row locks, сами открывают транзакции и рассчитаны на PostgreSQL.

## Production checklist

- `DJANGO_DEBUG=false`;
- новый `DJANGO_SECRET_KEY`;
- точные `ALLOWED_HOSTS`;
- ограниченный CORS вместо `CORS_ALLOW_ALL_ORIGINS`;
- PostgreSQL и резервное копирование;
- TLS на reverse proxy;
- защита или отключение `/api/reset`;
- отдельное хранение секретов Green API;
- production frontend build через `npm run build`;
- проверка `npm audit` и плановое обновление Next.js.

## Troubleshooting

### Frontend показывает Standalone Mode

Проверьте:

1. backend запущен на порту 4000;
2. `GET http://localhost:4000/api/health` отвечает 200;
3. `NEXT_PUBLIC_API_URL` заканчивается на `/api`;
4. порт или запрос не блокируется firewall.

После восстановления API Header автоматически вернется в `API 4000 LIVE`.

### Нет demo-данных

Запустите `manage.py migrate`, затем `manage.py seed_demo`.

### Webhook отвечает 200, но нет сообщения

Проверьте тип события, `idInstance`, chat ID и настройки `MOCK_GREEN_API`. Повторный `idMessage` намеренно игнорируется.

### Изменения моделей не применились

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```
