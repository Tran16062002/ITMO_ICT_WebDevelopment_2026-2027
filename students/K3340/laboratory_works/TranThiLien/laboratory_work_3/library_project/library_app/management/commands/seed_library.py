"""
Заполнение БД демонстрационными данными:

    python manage.py seed_library          # добавить данные
    python manage.py seed_library --clear  # очистить таблицы и заполнить заново

Даты считаются от сегодняшнего дня, чтобы все аналитические запросы
и отчёт за текущий месяц сразу возвращали непустой результат.
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from library_app import services
from library_app.models import (Author, Book, BookCopy, BookCopyRoomHistory, BookLoan,
                                Publisher, Reader, ReaderRoomHistory, ReadingRoom, Section)


class Command(BaseCommand):
    help = 'Заполнить базу демонстрационными данными библиотеки'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить таблицы перед заполнением')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            for model in (BookLoan, BookCopyRoomHistory, ReaderRoomHistory, BookCopy,
                          Reader, Book, Author, Publisher, Section, ReadingRoom):
                model.objects.all().delete()
        if ReadingRoom.objects.exists():
            self.stdout.write(self.style.WARNING('Данные уже есть. Используйте --clear.'))
            return

        today = timezone.localdate()
        ago = lambda **kw: today - relativedelta(**kw)

        # --- Залы ---
        r1 = ReadingRoom.objects.create(room_number='1', name='Общий читальный зал', capacity=60)
        r2 = ReadingRoom.objects.create(room_number='2', name='Зал научной литературы', capacity=30)
        r3 = ReadingRoom.objects.create(room_number='3', name='Детский зал', capacity=25)

        # --- Справочники ---
        fiction = Section.objects.create(name='Художественная литература')
        science = Section.objects.create(name='Научная литература')
        it = Section.objects.create(name='Информационные технологии')

        eksmo = Publisher.objects.create(name='Эксмо')
        piter = Publisher.objects.create(name='Питер')
        nauka = Publisher.objects.create(name='Наука')

        tolstoy = Author.objects.create(full_name='Толстой Лев Николаевич')
        pushkin = Author.objects.create(full_name='Пушкин Александр Сергеевич')
        knuth = Author.objects.create(full_name='Кнут Дональд')
        tanenbaum = Author.objects.create(full_name='Таненбаум Эндрю')
        bos = Author.objects.create(full_name='Бос Херберт')
        landau = Author.objects.create(full_name='Ландау Лев Давидович')
        lifshitz = Author.objects.create(full_name='Лифшиц Евгений Михайлович')

        # --- Книги ---
        def book(title, publisher, section, year, cipher, authors):
            b = Book.objects.create(title=title, publisher=publisher, section=section,
                                    publication_year=year, cipher=cipher)
            b.authors.set(authors)
            return b

        war = book('Война и мир', eksmo, fiction, 2020, '84(2Рос)1-44', [tolstoy])
        onegin = book('Евгений Онегин', eksmo, fiction, 2019, '84(2Рос)1-5', [pushkin])
        taocp = book('Искусство программирования. Том 1', piter, it, 2018, '32.973-018', [knuth])
        os_book = book('Современные операционные системы', piter, it, 2021, '32.973.26', [tanenbaum, bos])
        mech = book('Теоретическая физика. Механика', nauka, science, 1988, '22.311', [landau, lifshitz])

        # --- Экземпляры (поступление через сервис: создаётся история зала) ---
        counter = iter(range(1, 1000))

        def copies(b, room, n, received):
            return [services.receive_copy({'book': b, 'current_room': room,
                                           'inventory_number': f'INV-{next(counter):04d}',
                                           'received_date': received})
                    for _ in range(n)]

        war_c = copies(war, r1, 4, ago(years=2))
        onegin_c = copies(onegin, r3, 3, ago(years=1, months=6))
        taocp_c = copies(taocp, r2, 2, ago(years=1))          # редкая книга: 2 экземпляра
        os_c = copies(os_book, r2, 3, ago(months=8))
        mech_c = copies(mech, r2, 1, ago(years=3))            # редкая книга: 1 экземпляр

        # Перерегистрация экземпляра в другом зале и списание
        services.move_copy(war_c[3], r2, day=ago(days=10))
        services.write_off_copy(os_c[2], 'lost', day=ago(days=5))

        # --- Читатели (запись через сервис: создаётся история зала) ---
        def reader(ticket, name, passport, birth, education, degree, room, registered):
            return services.register_reader({
                'ticket_number': ticket, 'full_name': name, 'passport_number': passport,
                'birth_date': birth, 'address': 'г. Санкт-Петербург, Кронверкский пр., 49',
                'phone': f'+7-911-000-{ticket[-2:]}', 'education': education,
                'has_academic_degree': degree, 'current_room': room,
                'registration_date': registered,
            })

        ivanov = reader('T-0001', 'Иванов Иван Иванович', '4010 123401', ago(years=35),
                        'higher', True, r2, ago(years=2))
        petrova = reader('T-0002', 'Петрова Анна Сергеевна', '4010 123402', ago(years=19),
                         'secondary', False, r1, ago(months=6))
        sidorov = reader('T-0003', 'Сидоров Павел Олегович', '4010 123403', ago(years=17),
                         'primary', False, r3, ago(days=12))
        kuznetsova = reader('T-0004', 'Кузнецова Мария Ивановна', '4010 123404', ago(years=45),
                            'higher', False, r1, ago(years=1, months=3))   # без перерегистрации
        smirnov = reader('T-0005', 'Смирнов Олег Петрович', '4010 123405', ago(years=28),
                         'higher', False, r2, ago(days=3))

        # Перерегистрация (Иванов прошёл её недавно) и перевод в другой зал
        services.reregister_reader(ivanov, 'T-1001', day=ago(months=2))
        services.move_reader(petrova, r2, day=ago(days=7))

        # --- Выдачи ---
        BookLoan.objects.create(book_copy=war_c[0], reader=petrova, loan_date=ago(months=2))   # > месяца
        BookLoan.objects.create(book_copy=taocp_c[0], reader=ivanov, loan_date=ago(days=10))   # редкая
        BookLoan.objects.create(book_copy=mech_c[0], reader=smirnov, loan_date=ago(days=2))    # редкая
        BookLoan.objects.create(book_copy=onegin_c[0], reader=sidorov, loan_date=ago(days=40)) # > месяца
        BookLoan.objects.create(book_copy=war_c[1], reader=kuznetsova, loan_date=ago(months=3),
                                return_date=ago(months=2))                                    # возвращена

        self.stdout.write(self.style.SUCCESS(
            f'Готово: залов {ReadingRoom.objects.count()}, книг {Book.objects.count()}, '
            f'экземпляров {BookCopy.objects.count()}, читателей {Reader.objects.count()}, '
            f'выдач {BookLoan.objects.count()}'))
