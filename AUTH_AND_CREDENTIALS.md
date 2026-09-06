# Heap Analytics Connector — Auth & Credentials Standard

**Compliance:** AUTH_AND_CREDENTIALS_STANDARD.md (B1–B10)

## Схема аутентификации
- **Метод:** Heap App ID + Environment API Key
- **Хранение:** Секреты сохраняются изолированно в хранилище секретов платформы Imperal.
- **Валидация:** При сохранении ключа выполняется тестовый запрос `GET /api/v1/event_definitions`.
- **Отключение:** Удаление локальных ключей без воздействия на аккаунт вендора.
