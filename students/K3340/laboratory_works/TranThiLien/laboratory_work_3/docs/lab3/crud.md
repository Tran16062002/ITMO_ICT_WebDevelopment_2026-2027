# CRUD

Реализовано через generic-классы DRF: `ListCreateAPIView` для списка и создания,
`RetrieveUpdateDestroyAPIView` (или `RetrieveUpdateAPIView`) для одного объекта.

| Ресурс | Список / создание | Один объект | Методы одного объекта |
| --- | --- | --- | --- |
| Залы | `/api/rooms/` | `/api/rooms/{id}/` | GET, PUT, PATCH, DELETE |
| Разделы | `/api/sections/` | `/api/sections/{id}/` | GET, PUT, PATCH, DELETE |
| Издательства | `/api/publishers/` | `/api/publishers/{id}/` | GET, PUT, PATCH, DELETE |
| Авторы | `/api/authors/` | `/api/authors/{id}/` | GET, PUT, PATCH, DELETE |
| Книги | `/api/books/` | `/api/books/{id}/` | GET, PUT, PATCH, DELETE |
| Экземпляры | `/api/copies/` | `/api/copies/{id}/` | GET, PUT, PATCH (без DELETE) |
| Читатели | `/api/readers/` | `/api/readers/{id}/` | GET, PUT, PATCH, DELETE |
| Выдачи | `/api/loans/` | `/api/loans/{id}/` | GET, PUT, PATCH, DELETE |

Удаление объекта, на который ссылаются другие записи (например, зала с читателями),
возвращает `409 Conflict`.

## Залы

```http
POST /api/rooms/
{"room_number": "4", "name": "Зал периодики", "capacity": 20}
```

## Книги

`authors` — список id авторов. Переклассификация — смена шифра:

```http
POST /api/books/
{"title": "Война и мир", "publisher": 1, "section": 1,
 "publication_year": 2020, "cipher": "84(2Рос)1-44", "authors": [1]}

PATCH /api/books/1/
{"cipher": "84(2Рос=Рус)1-44"}
```

## Экземпляры — принять книгу в фонд

При создании автоматически открывается запись истории зала.

```http
POST /api/copies/
{"book": 3, "inventory_number": "INV-0100", "current_room": 2}
```

```json
{"id": 14, "inventory_number": "INV-0100", "status": "available",
 "received_date": "2026-11-26", "write_off_date": null, "write_off_reason": "",
 "book": 3, "current_room": 2}
```

При PUT/PATCH поля `book`, `current_room`, `status` не меняются: для них есть операции
`move` и `write-off` (см. «Операции библиотекаря»). `DELETE` не поддерживается —
вместо удаления экземпляр списывается.

## Читатели — записать нового читателя

```http
POST /api/readers/
{"ticket_number": "T-0006", "full_name": "Новиков Илья Сергеевич",
 "passport_number": "4010 999999", "birth_date": "2008-05-01",
 "address": "г. Санкт-Петербург", "phone": "+7-900-000-00-00",
 "education": "secondary", "has_academic_degree": false, "current_room": 1}
```

- `registration_date` по умолчанию — сегодня; открывается запись истории зала.
- При PUT/PATCH не меняются `current_room`, `ticket_number`, `status`
  (для них операции `move`, `reregister` и выписка).
- `DELETE /api/readers/{id}/` — **выписка** читателя: `status = "excluded"`,
  заполняется `exclusion_date`, запись не удаляется. Ответ `204`.
- Фильтр списка: `GET /api/readers/?status=active` или `?status=excluded`.

## Выдачи — закрепить книгу за читателем

```http
POST /api/loans/
{"book_copy": 14, "reader": 6}
```

Проверяется: экземпляр не списан и не на руках, читатель активен. Иначе `400`:

```json
{"non_field_errors": ["Экземпляр уже на руках у другого читателя."]}
```

Возврат книги:

```http
PATCH /api/loans/6/
{"return_date": "2026-11-27"}
```

Фильтр: `GET /api/loans/?active=1` — только книги на руках.
