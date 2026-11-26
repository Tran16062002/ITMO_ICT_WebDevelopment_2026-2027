# Модель данных

10 моделей Django (11 таблиц вместе с автоматической `BOOK_AUTHOR`).
Фонд учитывается по физическим экземплярам (`BookCopy`), история залов хранится
отдельно для экземпляров и для читателей — это нужно для отчёта «на каждый день».

## Таблицы

| Модель | Назначение | Ключевые поля |
| --- | --- | --- |
| `ReadingRoom` | читальный зал | `room_number` (UQ), `name`, `capacity` |
| `Section` | раздел фонда | `name` (UQ) |
| `Publisher` | издательство | `name` (UQ) |
| `Author` | автор | `full_name` |
| `Book` | книга (издание) | `title`, `publication_year`, `cipher` (UQ), FK `publisher`, FK `section`, M:N `authors` |
| `BookCopy` | экземпляр книги | `inventory_number` (UQ), FK `book`, FK `current_room`, `status`, `received_date`, `write_off_date`, `write_off_reason` |
| `BookCopyRoomHistory` | история залов экземпляра | FK `book_copy`, FK `room`, `start_date`, `end_date` |
| `Reader` | читатель | `ticket_number` (UQ), `full_name`, `passport_number` (UQ), `birth_date`, `address`, `phone`, `education`, `has_academic_degree`, FK `current_room`, `status`, `registration_date`, `reregistration_date`, `exclusion_date` |
| `ReaderRoomHistory` | история залов читателя | FK `reader`, FK `room`, `start_date`, `end_date` |
| `BookLoan` | закрепление экземпляра за читателем | FK `book_copy`, FK `reader`, `loan_date`, `return_date` |

## Связи и related_name

| Связь | Тип | related_name |
| --- | --- | --- |
| Book — Author | M:N (`ManyToManyField`, таблица `BOOK_AUTHOR`) | `author.books` |
| Reader — BookCopy | M:N through `BookLoan` | `copy.readers`, `reader.loans`, `copy.loans` |
| Publisher → Book | 1:N | `publisher.books` |
| Section → Book | 1:N | `section.books` |
| Book → BookCopy | 1:N | `book.copies` |
| ReadingRoom → BookCopy | 1:N | `room.book_copies` |
| ReadingRoom → Reader | 1:N | `room.readers` |
| BookCopy → BookCopyRoomHistory | 1:N | `copy.room_history` |
| Reader → ReaderRoomHistory | 1:N | `reader.room_history` |

## Значения перечислимых полей

| Поле | Значения |
| --- | --- |
| `BookCopy.status` | `available` — в фонде, `written_off` — списан |
| `BookCopy.write_off_reason` | `old` — ветхий, `lost` — утерян |
| `Reader.status` | `active` — активен, `excluded` — исключён |
| `Reader.education` | `primary`, `secondary`, `higher` |

## Правила

- Шифр (`cipher`) принадлежит изданию, инвентарный номер — экземпляру.
- Экземпляр на руках, пока у выдачи пустая `return_date`.
- Списание и выписка не удаляют записи, а меняют `status` — отчёты за прошлые месяцы не меняются.
- `end_date` в истории — последний день в зале включительно; при событии в день `D`
  старая запись закрывается датой `D − 1`, новая открывается датой `D`.
