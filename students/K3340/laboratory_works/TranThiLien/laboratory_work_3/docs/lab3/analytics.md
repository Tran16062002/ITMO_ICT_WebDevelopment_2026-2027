# Аналитические запросы

| № | Вопрос из задания | URL |
| --- | --- | --- |
| 1 | Какие книги закреплены за заданным читателем? | `GET /api/readers/{id}/books/` |
| 2 | Кто из читателей взял книгу более месяца тому назад? | `GET /api/analytics/overdue-readers/` |
| 3 | За кем закреплены книги, экземпляров которых не больше 2? | `GET /api/analytics/rare-book-readers/?max_copies=2` |
| 4 | Сколько в библиотеке читателей младше 20 лет? | `GET /api/analytics/young-readers/?age=20` |
| 5 | Процент читателей по образованию и с учёной степенью | `GET /api/analytics/education/` |

Запрос 1 описан в разделе «Вложенные объекты».

## 2. Читатели, взявшие книгу более месяца назад

Учитываются только невозвращённые книги, граница — календарный месяц от сегодняшней даты.

```python
border = today - relativedelta(months=1)
Reader.objects.filter(loans__return_date__isnull=True,
                      loans__loan_date__lt=border).distinct()
```

```json
{"border_date": "2026-10-26", "count": 2,
 "readers": [
   {"id": 2, "ticket_number": "T-0002", "full_name": "Петрова Анна Сергеевна",
    "phone": "+7-911-000-02",
    "loans": [{"id": 1, "loan_date": "2026-09-26", "inventory_number": "INV-0001",
               "room": "Зал 1 «Общий читальный зал»",
               "book": {"id": 1, "title": "Война и мир", "cipher": "84(2Рос)1-44",
                        "publication_year": 2020}}]}
 ]}
```

## 3. Читатели с книгами, экземпляров которых не больше N

Считаются экземпляры в фонде (`status = available`). Параметр `max_copies`, по умолчанию 2.

```python
rare_books = (Book.objects
              .annotate(n=Count('copies', filter=Q(copies__status='available')))
              .filter(n__lte=max_copies).values('id'))
Reader.objects.filter(loans__return_date__isnull=True,
                      loans__book_copy__book__in=rare_books).distinct()
```

Ответ имеет тот же вид, что в запросе 2: читатели и их выдачи редких книг.

## 4. Читатели младше N лет

Учитываются активные читатели. Параметр `age`, по умолчанию 20.

```python
Reader.objects.filter(status='active',
                      birth_date__gt=today - relativedelta(years=age)).count()
```

```json
{"age": 20, "count": 2}
```

## 5. Процентное распределение по образованию

Учитываются активные читатели. Учёная степень — отдельный признак, поэтому её процент
считается от общего числа и не входит в сумму 100 %.

```python
Reader.objects.filter(status='active').aggregate(
    total=Count('id'),
    primary=Count('id', filter=Q(education='primary')),
    secondary=Count('id', filter=Q(education='secondary')),
    higher=Count('id', filter=Q(education='higher')),
    academic_degree=Count('id', filter=Q(has_academic_degree=True)),
)
```

```json
{"total": 5,
 "count": {"primary": 1, "secondary": 1, "higher": 3, "academic_degree": 1},
 "percent": {"primary": 20.0, "secondary": 20.0, "higher": 60.0, "academic_degree": 20.0}}
```
