# QORJYN API

Локальный базовый URL: `http://localhost:4000/api`.

Frontend переопределяет адрес через `NEXT_PUBLIC_API_URL`.

## Общие правила

- JSON-поля во внешнем контракте используют `camelCase`.
- Успех: `{"success": true, ...}`.
- Ошибка: `{"success": false, "error": "Описание"}` со статусом `400` или `500`.
- Авторизация пользовательского API пока не применяется.
- Query-параметры передаются в `camelCase` и не преобразуются автоматически.

## Маршруты

| Метод | Маршрут | Назначение |
|---|---|---|
| GET | `/health` | Состояние API и версия приложения |
| POST | `/reset` | Восстановление demo-данных |
| GET, POST | `/inventory` | Остатки и изменение количества |
| POST | `/tender` | Предложения поставщиков |
| GET | `/forecast` | Прогноз расхода товара |
| GET, POST, PATCH | `/orders` | Список, создание и смена статуса заказов |
| GET | `/suppliers` | Поставщики и цены |
| GET, POST | `/waves` | Закупочные волны и участие |
| GET, POST | `/rescue` | Соседские резервы |
| GET | `/dashboard` | KPI, графики и риски |
| GET | `/activity` | Последние события бизнеса |
| GET | `/metrics` | Накопленные метрики ценности |
| POST | `/webhook/greenapi` | Входящий webhook Green API |
| POST | `/onboarding` | Создание бизнеса и его точек |
| GET | `/tools` | Каталог инструментов |
| POST | `/tools/favorite` | Избранные инструменты бизнеса |

## Health check

```http
GET /api/health
```

```json
{
  "success": true,
  "appVersion": "1.0.0"
}
```

## Остатки

### Получение

```http
GET /api/inventory?businessId=biz-001&status=critical
```

Доступные фильтры: `businessId`, `locationId`, `productId`, `status`.

Ответ содержит `inventory`, `products` и `locations`. Каждый элемент остатка включает вложенные `product`, `location` и вычисляемое поле `daysRemaining`.

### Изменение

```http
POST /api/inventory
Content-Type: application/json

{
  "productId": "prod-001",
  "locationId": "loc-001",
  "delta": -1,
  "source": "manual",
  "note": "Ручная корректировка"
}
```

`delta` положительный для прихода и отрицательный для расхода. Отрицательный итоговый остаток запрещен.

## Тендер

```http
POST /api/tender
Content-Type: application/json

{
  "productId": "prod-001",
  "quantity": 50
}
```

Ответ содержит массив `offers` и строку `aiExplanation`.

## Прогноз

```http
GET /api/forecast?productId=prod-001&locationId=loc-001
```

Ответ `forecast` содержит срок до дефицита, рекомендуемый объем заказа, факторы и семидневный прогноз.

## Заказы

### Список

```http
GET /api/orders?businessId=biz-001
```

### Создание

```http
POST /api/orders
Content-Type: application/json

{
  "businessId": "biz-001",
  "supplierId": "sup-001",
  "items": [
    {"productId": "prod-001", "quantity": 20}
  ],
  "source": "manual"
}
```

`source`: `manual`, `auto_order`, `wave` или `tender`.

### Смена статуса

```http
PATCH /api/orders
Content-Type: application/json

{
  "orderId": "ord-001",
  "status": "delivered",
  "note": "Доставка принята"
}
```

Статусы: `pending`, `confirmed`, `preparing`, `in_transit`, `delivered`, `issue`.

## Поставщики

```http
GET /api/suppliers
```

`basePrice` — объект, где ключом служит ID товара, например `{"prod-001": 450}`.

## Закупочные волны

```http
GET /api/waves
```

Присоединение:

```json
{
  "action": "join",
  "waveId": "wave-001",
  "businessId": "biz-001",
  "quantity": 40
}
```

Выход:

```json
{
  "action": "leave",
  "waveId": "wave-001",
  "businessId": "biz-001"
}
```

Оба запроса отправляются через `POST /api/waves`.

## Соседский резерв

```http
GET /api/rescue?businessId=biz-001
```

```http
POST /api/rescue
Content-Type: application/json

{
  "action": "accept",
  "transferId": "rescue-001"
}
```

Допустимые действия: `accept`, `decline`. Принятие выполняет складские проводки в одной транзакции и завершает transfer со статусом `completed`.

## Dashboard, активность и метрики

```http
GET /api/dashboard?businessId=biz-001
GET /api/activity?businessId=biz-001&limit=10
GET /api/metrics
```

## Onboarding

```http
POST /api/onboarding
Content-Type: application/json

{
  "name": "Новая кофейня",
  "businessType": "coffee",
  "district": "Алмалинский",
  "phone": "77010000000",
  "contactName": "Алия",
  "logoEmoji": "☕",
  "allowSurplusSharing": true,
  "locations": [
    {
      "name": "Основная точка",
      "address": "ул. Абая, 1",
      "lat": 43.238,
      "lng": 76.945
    }
  ],
  "categories": ["dairy", "coffee"]
}
```

`businessType`: `coffee`, `bakery`, `minimarket`, `restaurant`, `pharmacy`, `flower`.

Бизнес и все точки создаются атомарно. Ответ также содержит `recommendedThresholds` и `recommendedTools`.

## Каталог инструментов

```http
GET /api/tools?category=warehouse&businessType=coffee&businessId=biz-001
```

Избранное:

```http
POST /api/tools/favorite
Content-Type: application/json

{
  "businessId": "biz-001",
  "toolCode": "forecast",
  "favorite": true
}
```

## Green API webhook

```http
POST /api/webhook/greenapi
Content-Type: application/json
```

URL указывается в Green API как `https://<public-host>/api/webhook/greenapi`. Дубликаты `idMessage` игнорируются. В локальной среде используйте `MOCK_GREEN_API=true`.

## Reset demo

```http
POST /api/reset
```

Маршрут пересоздает demo-данные и не должен оставаться публично доступным без защиты в production.
