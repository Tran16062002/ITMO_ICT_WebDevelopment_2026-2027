# Отчёт о работе библиотеки за месяц

```http
GET /api/reports/monthly/?year=2026&month=11
```

Параметры `year` и `month` необязательны: по умолчанию — текущий месяц.

## Содержание отчёта

- количество книг (экземпляров) и читателей **на каждый день** в каждом из залов
  и в библиотеке в целом;
- количество читателей, записавшихся за отчётный месяц, в каждый зал и в библиотеку в целом.

## Как считается

Состояние на день `d` берётся из таблиц истории: запись действует, если
`start_date <= d` и (`end_date` пустая или `end_date >= d`).

```python
on_day = Q(start_date__lte=d) & (Q(end_date__isnull=True) | Q(end_date__gte=d))

# экземпляры по залам
BookCopyRoomHistory.objects.filter(on_day) \
    .values_list('room').annotate(n=Count('book_copy', distinct=True))

# читатели по залам
ReaderRoomHistory.objects.filter(on_day) \
    .values_list('room').annotate(n=Count('reader', distinct=True))

# записавшиеся за месяц: зал первой записи истории
ReaderRoomHistory.objects.filter(start_date=F('reader__registration_date'),
                                 start_date__year=year, start_date__month=month) \
    .values_list('room').annotate(n=Count('reader', distinct=True))
```

## Пример ответа (сокращённо)

```json
{
  "year": 2026, "month": 11,
  "days": [
    {"date": "2026-11-01",
     "rooms": [
       {"room_id": 1, "room_number": "1", "room": "Общий читальный зал", "books": 4, "readers": 2},
       {"room_id": 2, "room_number": "2", "room": "Зал научной литературы", "books": 6, "readers": 1},
       {"room_id": 3, "room_number": "3", "room": "Детский зал", "books": 3, "readers": 0}
     ],
     "total": {"books": 13, "readers": 3}}
  ],
  "registered": {
    "by_room": [
      {"room_id": 1, "room_number": "1", "room": "Общий читальный зал", "count": 0},
      {"room_id": 2, "room_number": "2", "room": "Зал научной литературы", "count": 1},
      {"room_id": 3, "room_number": "3", "room": "Детский зал", "count": 2}
    ],
    "total": 3
  }
}
```
