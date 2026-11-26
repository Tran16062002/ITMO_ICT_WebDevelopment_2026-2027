# GET-запросы с вложенными объектами

| URL | Связь | Что возвращает |
| --- | --- | --- |
| `GET /api/rooms/{id}/readers/` | 1:N `room.readers` | зал и его активные читатели |
| `GET /api/books/{id}/full/` | M:N `authors` + 1:N `copies` | книга с издательством, разделом, авторами и экземплярами |
| `GET /api/authors/{id}/books/` | M:N, обратная сторона `author.books` | автор и его книги |
| `GET /api/readers/{id}/books/` | M:N через `BookLoan` | экземпляры на руках у читателя |
| `GET /api/copies/{id}/history/` | 1:N `copy.room_history` | история залов экземпляра |
| `GET /api/readers/{id}/history/` | 1:N `reader.room_history` | история залов читателя |

## Зал и его читатели (1:N)

```http
GET /api/rooms/2/readers/
```

```json
{"id": 2, "room_number": "2", "name": "Зал научной литературы", "capacity": 30,
 "readers": [
   {"id": 1, "ticket_number": "T-1001", "full_name": "Иванов Иван Иванович",
    "phone": "+7-911-000-01", "status": "active"},
   {"id": 5, "ticket_number": "T-0005", "full_name": "Смирнов Олег Петрович",
    "phone": "+7-911-000-05", "status": "active"}
 ]}
```

## Полная информация о книге (M:N и 1:N)

```http
GET /api/books/2/full/
```

```json
{"id": 2, "title": "Евгений Онегин", "cipher": "84(2Рос)1-5", "publication_year": 2019,
 "publisher": {"id": 1, "name": "Эксмо"},
 "section": {"id": 1, "name": "Художественная литература"},
 "authors": [{"id": 2, "full_name": "Пушкин Александр Сергеевич"}],
 "copies_in_fund": 3,
 "copies": [
   {"id": 5, "inventory_number": "INV-0005", "current_room": "Зал 3 «Детский зал»",
    "status": "В фонде", "received_date": "2025-05-26"}
 ]}
```

## Автор и его книги (M:N, обратная сторона)

```http
GET /api/authors/4/books/
```

```json
{"id": 4, "full_name": "Таненбаум Эндрю",
 "books": [{"id": 4, "title": "Современные операционные системы",
            "cipher": "32.973.26", "publication_year": 2021}]}
```

## Книги, закреплённые за читателем (M:N через BookLoan)

Это также запрос 1 из задания.

```http
GET /api/readers/2/books/
```

```json
[{"id": 1, "loan_date": "2026-09-26", "inventory_number": "INV-0001",
  "room": "Зал 1 «Общий читальный зал»",
  "book": {"id": 1, "title": "Война и мир", "cipher": "84(2Рос)1-44",
           "publication_year": 2020}}]
```
