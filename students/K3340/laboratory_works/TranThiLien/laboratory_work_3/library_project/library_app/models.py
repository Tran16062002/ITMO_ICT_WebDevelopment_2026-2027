from django.db import models
from django.utils import timezone


class ReadingRoom(models.Model):
    """Читальный зал"""
    room_number = models.CharField('Номер зала', max_length=10, unique=True)
    name = models.CharField('Название', max_length=100)
    capacity = models.PositiveIntegerField('Вместимость (чел.)')

    class Meta:
        verbose_name = 'Читальный зал'
        verbose_name_plural = 'Читальные залы'
        ordering = ['room_number']

    def __str__(self):
        return f'Зал {self.room_number} «{self.name}»'


class Section(models.Model):
    """Раздел фонда"""
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """Издательство"""
    name = models.CharField('Название', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Author(models.Model):
    """Автор"""
    full_name = models.CharField('ФИО', max_length=150)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Book(models.Model):
    """Книга как издание (наименование), а не физический экземпляр"""
    title = models.CharField('Название', max_length=255)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT,
                                  related_name='books', verbose_name='Издательство')
    section = models.ForeignKey(Section, on_delete=models.PROTECT,
                                related_name='books', verbose_name='Раздел')
    publication_year = models.PositiveSmallIntegerField('Год издания')
    # Шифр может измениться в результате переклассификации
    cipher = models.CharField('Шифр', max_length=30, unique=True)
    # M:N — Django создаёт таблицу BOOK_AUTHOR автоматически
    authors = models.ManyToManyField(Author, related_name='books', verbose_name='Авторы')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.cipher})'


class BookCopy(models.Model):
    """Физический экземпляр книги"""
    STATUS_AVAILABLE = 'available'
    STATUS_WRITTEN_OFF = 'written_off'
    STATUS = (
        (STATUS_AVAILABLE, 'В фонде'),
        (STATUS_WRITTEN_OFF, 'Списан'),
    )
    REASONS = (
        ('old', 'Ветхий'),
        ('lost', 'Утерян'),
    )

    book = models.ForeignKey(Book, on_delete=models.PROTECT,
                             related_name='copies', verbose_name='Книга')
    inventory_number = models.CharField('Инвентарный номер', max_length=30, unique=True)
    current_room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT,
                                     related_name='book_copies', verbose_name='Текущий зал')
    status = models.CharField('Статус', max_length=12, choices=STATUS, default=STATUS_AVAILABLE)
    received_date = models.DateField('Дата поступления', default=timezone.localdate)
    write_off_date = models.DateField('Дата списания', null=True, blank=True)
    write_off_reason = models.CharField('Причина списания', max_length=5,
                                        choices=REASONS, blank=True)

    class Meta:
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'
        ordering = ['inventory_number']

    def __str__(self):
        return f'{self.inventory_number} — {self.book.title}'

    @property
    def is_on_loan(self):
        return self.loans.filter(return_date__isnull=True).exists()


class BookCopyRoomHistory(models.Model):
    """История размещения экземпляра по залам"""
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE,
                                  related_name='room_history', verbose_name='Экземпляр')
    room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT,
                             related_name='copy_history', verbose_name='Зал')
    start_date = models.DateField('С')
    # null — экземпляр сейчас в этом зале; иначе последний день в зале включительно
    end_date = models.DateField('По', null=True, blank=True)

    class Meta:
        verbose_name = 'История залов экземпляра'
        verbose_name_plural = 'История залов экземпляров'
        ordering = ['book_copy', 'start_date']

    def __str__(self):
        return f'{self.book_copy.inventory_number}: {self.room} {self.start_date}–{self.end_date or "…"}'


class Reader(models.Model):
    """Читатель библиотеки"""
    EDUCATION = (
        ('primary', 'Начальное'),
        ('secondary', 'Среднее'),
        ('higher', 'Высшее'),
    )
    STATUS_ACTIVE = 'active'
    STATUS_EXCLUDED = 'excluded'
    STATUS = (
        (STATUS_ACTIVE, 'Активен'),
        (STATUS_EXCLUDED, 'Исключён'),
    )

    # Номер билета может измениться в результате перерегистрации
    ticket_number = models.CharField('Номер читательского билета', max_length=20, unique=True)
    full_name = models.CharField('ФИО', max_length=150)
    passport_number = models.CharField('Номер паспорта', max_length=20, unique=True)
    birth_date = models.DateField('Дата рождения')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    education = models.CharField('Образование', max_length=10, choices=EDUCATION)
    has_academic_degree = models.BooleanField('Учёная степень', default=False)
    current_room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT,
                                     related_name='readers', verbose_name='Текущий зал')
    status = models.CharField('Статус', max_length=10, choices=STATUS, default=STATUS_ACTIVE)
    registration_date = models.DateField('Дата записи', default=timezone.localdate)
    reregistration_date = models.DateField('Дата перерегистрации', null=True, blank=True)
    exclusion_date = models.DateField('Дата выписки', null=True, blank=True)
    # M:N Reader — BookCopy через ассоциативную сущность BookLoan
    copies = models.ManyToManyField(BookCopy, through='BookLoan',
                                    related_name='readers', verbose_name='Экземпляры на руках')

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} (билет {self.ticket_number})'


class ReaderRoomHistory(models.Model):
    """История закрепления читателя за залами"""
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE,
                               related_name='room_history', verbose_name='Читатель')
    room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT,
                             related_name='reader_history', verbose_name='Зал')
    start_date = models.DateField('С')
    end_date = models.DateField('По', null=True, blank=True)

    class Meta:
        verbose_name = 'История залов читателя'
        verbose_name_plural = 'История залов читателей'
        ordering = ['reader', 'start_date']

    def __str__(self):
        return f'{self.reader.full_name}: {self.room} {self.start_date}–{self.end_date or "…"}'


class BookLoan(models.Model):
    """Закрепление экземпляра книги за читателем"""
    book_copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT,
                                  related_name='loans', verbose_name='Экземпляр')
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT,
                               related_name='loans', verbose_name='Читатель')
    loan_date = models.DateField('Дата закрепления', default=timezone.localdate)
    # null — книга на руках у читателя
    return_date = models.DateField('Дата возврата', null=True, blank=True)

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'
        ordering = ['-loan_date']

    def __str__(self):
        return f'{self.book_copy} → {self.reader.full_name} ({self.loan_date})'
