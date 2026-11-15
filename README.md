# backend-moderation

HTTP API для модерации объявлений на FastAPI. Python 3.11+.

## Запуск

Из корня проекта в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\fastapi.exe dev
```

Сервис: http://127.0.0.1:8000. Документация API: http://127.0.0.1:8000/docs.
После активации окружения сервер запускается командой `fastapi dev`.

## API

`POST /predict` принимает JSON:

| Поле | Тип |
|---|---|
| `seller_id` | int |
| `is_verified_seller` | bool |
| `item_id` | int |
| `name` | str |
| `description` | str |
| `category` | int |
| `images_qty` | int, не меньше 0 |

Все поля обязательны. Типы проверяются без автоматического преобразования;
`null` и лишние поля отклоняются.

Ответ – JSON boolean: `true`, если есть нарушение, и `false`, если нарушения нет.
Верифицированный продавец проходит проверку независимо от количества фотографий.
Неверифицированный – только при наличии хотя бы одной фотографии.

| HTTP-статус | Значение |
|---|---|
| 200 | Проверка выполнена; тело ответа – `true` или `false` |
| 400 | Некорректный JSON, отсутствующее поле или неверное значение |
| 500 | Внутренняя ошибка сервиса |

Пример запроса – [example_request.json](example_request.json).
Неверифицированный продавец без фотографий получает `200` и `true`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" --data-binary '@example_request.json'
```

## Структура

- `routers/` – HTTP-обработчик.
- `services/` – правило модерации.
- `repositories/` – хранение последнего результата по `item_id` в памяти процесса.
- `schemas.py` – валидация входных данных.
- `main.py` – приложение и обработка ошибок.

Результаты проверок сбрасываются при перезапуске сервиса.

## Тесты

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

Тесты проверяют правило модерации, тип и обязательность полей, ошибки 400/500,
HTTP-контракт и работу репозитория. Ошибки сервиса и хранилища воспроизводятся
подменой зависимостей.
