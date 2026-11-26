"""
Бизнес-операции библиотекаря.

Каждая операция меняет «текущее» поле (current_room, status) и таблицу
истории в одной транзакции, чтобы они не расходились.

Соглашение по датам истории: end_date — последний день в зале включительно.
Если событие (перевод, списание, выписка) происходит в день D, старая
запись закрывается датой D - 1, новая открывается датой D.
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import (BookCopy, BookCopyRoomHistory, Reader, ReaderRoomHistory)


def _close_open_history(history_qs, day):
    history_qs.filter(end_date__isnull=True).update(end_date=day - timedelta(days=1))


def _move_history(history_qs, day, **new_record):
    """
    Закрыть открытую запись и открыть новую с даты day.
    Если открытая запись начата в тот же день — просто меняем в ней зал,
    чтобы не появлялся интервал с end_date < start_date.
    """
    model = history_qs.model
    same_day = history_qs.filter(end_date__isnull=True, start_date=day).first()
    if same_day:
        same_day.room = new_record['room']
        same_day.save(update_fields=['room'])
        return same_day
    _close_open_history(history_qs, day)
    return model.objects.create(start_date=day, **new_record)


# ---------- Экземпляры ----------

@transaction.atomic
def receive_copy(validated_data):
    """Принять экземпляр в фонд: создаётся экземпляр и первая запись истории зала."""
    copy = BookCopy.objects.create(**validated_data)
    BookCopyRoomHistory.objects.create(
        book_copy=copy, room=copy.current_room, start_date=copy.received_date)
    return copy


@transaction.atomic
def move_copy(copy, room, day=None):
    """Перерегистрировать экземпляр в другом зале."""
    day = day or timezone.localdate()
    _move_history(copy.room_history, day, book_copy=copy, room=room)
    copy.current_room = room
    copy.save(update_fields=['current_room'])
    return copy


@transaction.atomic
def write_off_copy(copy, reason, day=None):
    """Списать старый или потерянный экземпляр (запись не удаляется)."""
    day = day or timezone.localdate()
    _close_open_history(copy.room_history, day)
    # Если экземпляр потерян читателем — закрываем выдачу
    copy.loans.filter(return_date__isnull=True).update(return_date=day)
    copy.status = BookCopy.STATUS_WRITTEN_OFF
    copy.write_off_date = day
    copy.write_off_reason = reason
    copy.save(update_fields=['status', 'write_off_date', 'write_off_reason'])
    return copy


# ---------- Читатели ----------

@transaction.atomic
def register_reader(validated_data):
    """Записать нового читателя: создаётся читатель и первая запись истории зала."""
    reader = Reader.objects.create(**validated_data)
    ReaderRoomHistory.objects.create(
        reader=reader, room=reader.current_room, start_date=reader.registration_date)
    return reader


@transaction.atomic
def move_reader(reader, room, day=None):
    """Переписать читателя в другой зал."""
    day = day or timezone.localdate()
    _move_history(reader.room_history, day, reader=reader, room=room)
    reader.current_room = room
    reader.save(update_fields=['current_room'])
    return reader


@transaction.atomic
def reregister_reader(reader, ticket_number, day=None):
    """Перерегистрация: новый номер билета и дата перерегистрации."""
    reader.ticket_number = ticket_number
    reader.reregistration_date = day or timezone.localdate()
    reader.save(update_fields=['ticket_number', 'reregistration_date'])
    return reader


@transaction.atomic
def exclude_reader(reader, day=None):
    """Выписать (исключить) читателя — мягкое удаление."""
    day = day or timezone.localdate()
    _close_open_history(reader.room_history, day)
    reader.status = Reader.STATUS_EXCLUDED
    reader.exclusion_date = day
    reader.save(update_fields=['status', 'exclusion_date'])
    return reader


def expired_readers(day=None):
    """Записались более года назад и не прошли перерегистрацию за последний год."""
    day = day or timezone.localdate()
    year_ago = day - relativedelta(years=1)
    return (Reader.objects
            .filter(status=Reader.STATUS_ACTIVE, registration_date__lt=year_ago)
            .filter(Q(reregistration_date__isnull=True) | Q(reregistration_date__lt=year_ago)))


@transaction.atomic
def exclude_expired_readers(day=None):
    day = day or timezone.localdate()
    readers = list(expired_readers(day))
    for reader in readers:
        exclude_reader(reader, day)
    return readers
