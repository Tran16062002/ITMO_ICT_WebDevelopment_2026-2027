from django.utils import timezone
from rest_framework import serializers

from . import services
from .models import (Author, Book, BookCopy, BookCopyRoomHistory, BookLoan,
                     Publisher, Reader, ReaderRoomHistory, ReadingRoom, Section)


# ======================= Справочники =======================

class ReadingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingRoom
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


# ======================= Книги =======================

class BookSerializer(serializers.ModelSerializer):
    """CRUD книги: связи передаются по id (authors — список id)."""

    class Meta:
        model = Book
        fields = '__all__'


class CopyInBookSerializer(serializers.ModelSerializer):
    current_room = serializers.StringRelatedField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = BookCopy
        fields = ['id', 'inventory_number', 'current_room', 'status', 'received_date']


class BookFullSerializer(serializers.ModelSerializer):
    """GET с вложенными объектами: M:N authors и 1:N copies."""
    authors = AuthorSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    section = SectionSerializer(read_only=True)
    copies = CopyInBookSerializer(many=True, read_only=True)
    copies_in_fund = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'cipher', 'publication_year', 'publisher', 'section',
                  'authors', 'copies_in_fund', 'copies']

    def get_copies_in_fund(self, obj):
        return obj.copies.filter(status=BookCopy.STATUS_AVAILABLE).count()


class BookShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'cipher', 'publication_year']


class AuthorWithBooksSerializer(serializers.ModelSerializer):
    """GET с вложенными объектами по обратной стороне M:N (author.books)."""
    books = BookShortSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'full_name', 'books']


# ======================= Экземпляры =======================

class BookCopySerializer(serializers.ModelSerializer):
    """
    POST — принять экземпляр в фонд.
    PUT/PATCH — правка инвентарного номера и даты поступления.
    Зал меняется только операцией move, статус — операцией write-off.
    """

    class Meta:
        model = BookCopy
        fields = '__all__'
        read_only_fields = ['status', 'write_off_date', 'write_off_reason']

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:  # при обновлении зал и книгу не меняем
            fields['current_room'].read_only = True
            fields['book'].read_only = True
        return fields

    def create(self, validated_data):
        return services.receive_copy(validated_data)


class BookCopyRoomHistorySerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField()

    class Meta:
        model = BookCopyRoomHistory
        fields = ['id', 'room', 'start_date', 'end_date']


# ======================= Читатели =======================

class ReaderSerializer(serializers.ModelSerializer):
    """
    POST — записать нового читателя.
    PUT/PATCH — правка личных данных.
    Зал, номер билета и статус меняются отдельными операциями.
    """

    class Meta:
        model = Reader
        exclude = ['copies']
        read_only_fields = ['status', 'reregistration_date', 'exclusion_date']

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields['current_room'].read_only = True
            fields['ticket_number'].read_only = True
        return fields

    def validate_birth_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('Дата рождения не может быть в будущем.')
        return value

    def create(self, validated_data):
        return services.register_reader(validated_data)


class ReaderShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = ['id', 'ticket_number', 'full_name', 'phone', 'status']


class ReadingRoomWithReadersSerializer(serializers.ModelSerializer):
    """GET с вложенными объектами 1:N (room.readers)."""
    readers = serializers.SerializerMethodField()

    class Meta:
        model = ReadingRoom
        fields = ['id', 'room_number', 'name', 'capacity', 'readers']

    def get_readers(self, obj):
        qs = obj.readers.filter(status=Reader.STATUS_ACTIVE)
        return ReaderShortSerializer(qs, many=True).data


class ReaderRoomHistorySerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField()

    class Meta:
        model = ReaderRoomHistory
        fields = ['id', 'room', 'start_date', 'end_date']


# ======================= Выдачи =======================

class BookLoanSerializer(serializers.ModelSerializer):
    """POST — закрепить экземпляр за читателем, PATCH return_date — возврат."""

    class Meta:
        model = BookLoan
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields['book_copy'].read_only = True
            fields['reader'].read_only = True
        return fields

    def validate(self, attrs):
        if self.instance is None:
            copy, reader = attrs['book_copy'], attrs['reader']
            if copy.status != BookCopy.STATUS_AVAILABLE:
                raise serializers.ValidationError('Экземпляр списан.')
            if copy.is_on_loan:
                raise serializers.ValidationError('Экземпляр уже на руках у другого читателя.')
            if reader.status != Reader.STATUS_ACTIVE:
                raise serializers.ValidationError('Читатель исключён из библиотеки.')
        loan_date = attrs.get('loan_date') or getattr(self.instance, 'loan_date', None)
        return_date = attrs.get('return_date')
        if loan_date and return_date and return_date < loan_date:
            raise serializers.ValidationError('Дата возврата раньше даты закрепления.')
        return attrs


class LoanWithBookSerializer(serializers.ModelSerializer):
    """Выдача с вложенными экземпляром и книгой (для /readers/{id}/books/)."""
    inventory_number = serializers.CharField(source='book_copy.inventory_number')
    book = BookShortSerializer(source='book_copy.book')
    room = serializers.StringRelatedField(source='book_copy.current_room')

    class Meta:
        model = BookLoan
        fields = ['id', 'loan_date', 'inventory_number', 'room', 'book']


class ReaderWithLoansSerializer(serializers.ModelSerializer):
    """Читатель + список выдач (используется в аналитике)."""
    loans = serializers.SerializerMethodField()

    class Meta:
        model = Reader
        fields = ['id', 'ticket_number', 'full_name', 'phone', 'loans']

    def get_loans(self, obj):
        loans = getattr(obj, 'selected_loans', None)
        if loans is None:
            loans = obj.loans.filter(return_date__isnull=True)
        return LoanWithBookSerializer(loans, many=True).data


# ======================= Параметры операций =======================

class MoveSerializer(serializers.Serializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ReadingRoom.objects.all())


class WriteOffSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=BookCopy.REASONS)


class ReregisterSerializer(serializers.Serializer):
    ticket_number = serializers.CharField(max_length=20)

    def validate_ticket_number(self, value):
        if Reader.objects.filter(ticket_number=value).exists():
            raise serializers.ValidationError('Читатель с таким номером билета уже есть.')
        return value
