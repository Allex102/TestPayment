### Локальный запуск

```bash
# Запуск всех сервисов
make up

# Остановка
make down

# Просмотр логов
make logs

# Применение миграций в Docker(при сборке автоматически проходят)
make migrate

# Создание миграции
make makemigration name="migration_name"
```

## 🧪 Тесты

```bash
# Запуск всех тестов
make test

Для ручного тестирования работоспособности брокера сообщений, достаточно создать платеж
```

## 🔍 Качество кода

```bash
# Проверка кода
make check

# Автоматическое форматирование и исправление
make fix
```

## 🐚 Дополнительно

```bash
# Python-shell внутри Docker
make docker-shell

# Подключение к PostgreSQL
make db
```
         
