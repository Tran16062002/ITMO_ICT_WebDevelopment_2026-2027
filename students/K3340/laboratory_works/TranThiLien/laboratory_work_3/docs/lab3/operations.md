# Операции библиотекаря

Каждая операция выполняется в одной транзакции: меняется «текущее» поле
и таблица истории.

| Операция из задания | Метод и URL | Тело запроса |
| --- | --- | --- |
| Записать нового читателя | `POST /api/readers/` | данные читателя (см. CRUD) |
| Принять книгу в фонд | `POST /api/copies/` | `book`, `inventory_number`, `current_room` |
| Списать старую или потерянную книгу | `POST /api/copies/{id}/write-off/` | `{"reason": "old" \| "lost"}` |
| Перерегистрировать книгу в другом зале | `POST /api/copies/{id}/move/` | `{"room": id}` |
| Переписать читателя в другой зал | `POST /api/readers/{id}/move/` | `{"room": id}` |
| Перерегистрация читателя (новый номер билета) | `POST /api/readers/{id}/reregister/` | `{"ticket_number": "..."}` |
| Выписать читателя | `DELETE /api/readers/{id}/` | — |
| Исключить не прошедших перерегистрацию | `GET` / `POST /api/readers/exclude-expired/` | — |

## Списание экземпляра

```http
POST /api/copies/14/write-off/
{"reason": "old"}
```

```json
{"id": 14, "inventory_number": "INV-0100", "status": "written_off",
 "received_date": "2026-11-26", "write_off_date": "2026-11-26",
 "write_off_reason": "old", "book": 3, "current_room": 2}
```

Запись истории зала закрывается; если экземпляр был на руках, выдача закрывается.
Повторное списание — `400 {"detail": "Экземпляр уже списан."}`.

## Перенос экземпляра в другой зал

```http
POST /api/copies/1/move/
{"room": 2}
```

История после переноса (`GET /api/copies/1/history/`):

```json
[{"id": 1, "room": "Зал 1 «Общий читальный зал»", "start_date": "2024-11-26", "end_date": "2026-11-25"},
 {"id": 16, "room": "Зал 2 «Зал научной литературы»", "start_date": "2026-11-26", "end_date": null}]
```

## Перерегистрация читателя

```http
POST /api/readers/6/reregister/
{"ticket_number": "T-2006"}
```

Меняет `ticket_number` и `reregistration_date`. Занятый номер — `400`:

```json
{"ticket_number": ["Читатель с таким номером билета уже есть."]}
```

## Исключение записавшихся более года назад без перерегистрации

Условие: `status = active`, `registration_date` раньше, чем год назад, и
`reregistration_date` пустая или тоже раньше, чем год назад.

- `GET /api/readers/exclude-expired/` — посмотреть, кто попадёт под исключение;
- `POST /api/readers/exclude-expired/` — исключить.

```json
{"excluded": 1,
 "readers": [{"id": 4, "ticket_number": "T-0004", "full_name": "Кузнецова Мария Ивановна",
              "phone": "+7-911-000-04", "status": "excluded"}]}
```
