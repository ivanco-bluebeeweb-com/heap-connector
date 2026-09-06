# Heap Analytics Connector — Connector Discovery

**Vendor API Baseline:** https://heap.io

## Архитектура API
- **Базовый адрес:** `https://heapanalytics.com/api`
- **Протокол:** REST / HTTPS (JSON)
- **Аутентификация:** Heap App ID + Environment API Key
- **Ключевые эндпоинты:**
  - определения событий (/event_definitions)
  - сегменты (/segments)
  - свойства пользователей (/user_properties)
- **Тестовая точка проверки подключения:** `GET /api/v1/event_definitions`.
