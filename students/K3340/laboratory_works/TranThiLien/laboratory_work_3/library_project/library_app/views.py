import calendar
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import (Author, Book, BookCopy, BookCopyRoomHistory, BookLoan,
                     Publisher, Reader, ReaderRoomHistory, ReadingRoom, Section)
from .serializers import (AuthorSerializer, AuthorWithBooksSerializer, BookCopyRoomHistorySerializer,
                          BookCopySerializer, BookFullSerializer, BookLoanSerializer, BookSerializer,
                          LoanWithBookSerializer, MoveSerializer, PublisherSerializer,
                          ReaderRoomHistorySerializer, ReaderSerializer, ReaderShortSerializer,
                          ReaderWithLoansSerializer, ReadingRoomSerializer,
                          ReadingRoomWithReadersSerializer, ReregisterSerializer,
                          SectionSerializer, WriteOffSerializer)


def int_param(request, name, default):
    try:
        return int(request.query_params.get(name, default))
    except (TypeError, ValueError):
        return default


# ============================================================
#                         CRUD
# ============================================================

class ReadingRoomListCreateView(generics.ListCreateAPIView):
    queryset = ReadingRoom.objects.all()
    serializer_class = ReadingRoomSerializer


class ReadingRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReadingRoom.objects.all()
    serializer_class = ReadingRoomSerializer


class SectionListCreateView(generics.ListCreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class PublisherListCreateView(generics.ListCreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class PublisherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH {"cipher": "..."} — переклассификация (смена шифра)."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookCopyListCreateView(generics.ListCreateAPIView):
    """POST — принять экземпляр книги в фонд библиотеки."""
    queryset = BookCopy.objects.select_related('book', 'current_room')
    serializer_class = BookCopySerializer


class BookCopyDetailView(generics.RetrieveUpdateAPIView):
    """Удаление не предусмотрено: вместо него — списание (write-off)."""
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer


class ReaderListCreateView(generics.ListCreateAPIView):
    """POST — записать в библиотеку нового читателя."""
    serializer_class = ReaderSerializer

    def get_queryset(self):
        qs = Reader.objects.select_related('current_room')
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class ReaderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """DELETE — выписать читателя (мягкое удаление, status='excluded')."""
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer

    def perform_destroy(self, instance):
        services.exclude_reader(instance)


class BookLoanListCreateView(generics.ListCreateAPIView):
    """POST — закрепить экземпляр за читателем."""
    serializer_class = BookLoanSerializer

    def get_queryset(self):
        qs = BookLoan.objects.select_related('book_copy', 'reader')
        if self.request.query_params.get('active') == '1':
            qs = qs.filter(return_date__isnull=True)
        return qs


class BookLoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH {"return_date": "YYYY-MM-DD"} — возврат книги."""
    queryset = BookLoan.objects.all()
    serializer_class = BookLoanSerializer


# ============================================================
#              GET с вложенными объектами
# ============================================================

class ReadingRoomReadersView(generics.RetrieveAPIView):
    """1:N — зал и его читатели."""
    queryset = ReadingRoom.objects.all()
    serializer_class = ReadingRoomWithReadersSerializer


class BookFullView(generics.RetrieveAPIView):
    """M:N authors + 1:N copies — полная информация о книге."""
    queryset = (Book.objects.select_related('publisher', 'section')
                .prefetch_related('authors', 'copies__current_room'))
    serializer_class = BookFullSerializer


class AuthorBooksView(generics.RetrieveAPIView):
    """M:N (обратная сторона) — автор и его книги."""
    queryset = Author.objects.prefetch_related('books')
    serializer_class = AuthorWithBooksSerializer


class ReaderBooksView(generics.ListAPIView):
    """Запрос 1: какие книги закреплены за заданным читателем (M:N через BookLoan)."""
    serializer_class = LoanWithBookSerializer

    def get_queryset(self):
        reader = get_object_or_404(Reader, pk=self.kwargs['pk'])
        return (reader.loans.filter(return_date__isnull=True)
                .select_related('book_copy__book', 'book_copy__current_room'))


class BookCopyHistoryView(generics.ListAPIView):
    serializer_class = BookCopyRoomHistorySerializer

    def get_queryset(self):
        copy = get_object_or_404(BookCopy, pk=self.kwargs['pk'])
        return copy.room_history.select_related('room')


class ReaderHistoryView(generics.ListAPIView):
    serializer_class = ReaderRoomHistorySerializer

    def get_queryset(self):
        reader = get_object_or_404(Reader, pk=self.kwargs['pk'])
        return reader.room_history.select_related('room')


# ============================================================
#                 Операции библиотекаря
# ============================================================

class BookCopyMoveView(APIView):
    """Перерегистрировать экземпляр в другом зале. Тело: {"room": id}"""

    def post(self, request, pk):
        copy = get_object_or_404(BookCopy, pk=pk)
        if copy.status != BookCopy.STATUS_AVAILABLE:
            return Response({'detail': 'Экземпляр списан.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.validated_data['room']
        if room == copy.current_room:
            return Response({'detail': 'Экземпляр уже в этом зале.'}, status=status.HTTP_400_BAD_REQUEST)
        services.move_copy(copy, room)
        return Response(BookCopySerializer(copy).data)


class BookCopyWriteOffView(APIView):
    """Списать старый или потерянный экземпляр. Тело: {"reason": "old" | "lost"}"""

    def post(self, request, pk):
        copy = get_object_or_404(BookCopy, pk=pk)
        if copy.status == BookCopy.STATUS_WRITTEN_OFF:
            return Response({'detail': 'Экземпляр уже списан.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WriteOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.write_off_copy(copy, serializer.validated_data['reason'])
        return Response(BookCopySerializer(copy).data)


class ReaderMoveView(APIView):
    """Переписать читателя в другой зал. Тело: {"room": id}"""

    def post(self, request, pk):
        reader = get_object_or_404(Reader, pk=pk, status=Reader.STATUS_ACTIVE)
        serializer = MoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.validated_data['room']
        if room == reader.current_room:
            return Response({'detail': 'Читатель уже закреплён за этим залом.'},
                            status=status.HTTP_400_BAD_REQUEST)
        services.move_reader(reader, room)
        return Response(ReaderSerializer(reader).data)


class ReaderReregisterView(APIView):
    """Перерегистрация читателя. Тело: {"ticket_number": "..."}"""

    def post(self, request, pk):
        reader = get_object_or_404(Reader, pk=pk, status=Reader.STATUS_ACTIVE)
        serializer = ReregisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.reregister_reader(reader, serializer.validated_data['ticket_number'])
        return Response(ReaderSerializer(reader).data)


class ExcludeExpiredReadersView(APIView):
    """
    GET  — посмотреть, кто будет исключён.
    POST — исключить записавшихся более года назад и не прошедших перерегистрацию.
    """

    def get(self, request):
        readers = services.expired_readers()
        return Response({'count': readers.count(),
                         'readers': ReaderShortSerializer(readers, many=True).data})

    def post(self, request):
        readers = services.exclude_expired_readers()
        return Response({'excluded': len(readers),
                         'readers': ReaderShortSerializer(readers, many=True).data})


# ============================================================
#                 Аналитические запросы
# ============================================================

class OverdueReadersView(APIView):
    """Запрос 2: кто из читателей взял книгу более месяца тому назад."""

    def get(self, request):
        border = timezone.localdate() - relativedelta(months=1)
        overdue = BookLoan.objects.filter(return_date__isnull=True, loan_date__lt=border) \
            .select_related('book_copy__book', 'book_copy__current_room')
        readers = (Reader.objects
                   .filter(loans__return_date__isnull=True, loans__loan_date__lt=border)
                   .distinct()
                   .prefetch_related(Prefetch('loans', queryset=overdue, to_attr='selected_loans')))
        return Response({'border_date': border,
                         'count': readers.count(),
                         'readers': ReaderWithLoansSerializer(readers, many=True).data})


class RareBookReadersView(APIView):
    """Запрос 3: за кем закреплены книги, экземпляров которых в библиотеке не больше N (по умолчанию 2)."""

    def get(self, request):
        max_copies = int_param(request, 'max_copies', 2)
        rare_books = (Book.objects
                      .annotate(n=Count('copies', filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
                      .filter(n__lte=max_copies)
                      .values('id'))
        rare_loans = BookLoan.objects.filter(return_date__isnull=True,
                                             book_copy__book__in=rare_books) \
            .select_related('book_copy__book', 'book_copy__current_room')
        readers = (Reader.objects
                   .filter(loans__return_date__isnull=True, loans__book_copy__book__in=rare_books)
                   .distinct()
                   .prefetch_related(Prefetch('loans', queryset=rare_loans, to_attr='selected_loans')))
        return Response({'max_copies': max_copies,
                         'count': readers.count(),
                         'readers': ReaderWithLoansSerializer(readers, many=True).data})


class YoungReadersView(APIView):
    """Запрос 4: сколько в библиотеке читателей младше N лет (по умолчанию 20)."""

    def get(self, request):
        age = int_param(request, 'age', 20)
        border = timezone.localdate() - relativedelta(years=age)
        count = Reader.objects.filter(status=Reader.STATUS_ACTIVE, birth_date__gt=border).count()
        return Response({'age': age, 'count': count})


class EducationStatsView(APIView):
    """Запрос 5: процент читателей с начальным, средним, высшим образованием и учёной степенью."""

    def get(self, request):
        stats = Reader.objects.filter(status=Reader.STATUS_ACTIVE).aggregate(
            total=Count('id'),
            primary=Count('id', filter=Q(education='primary')),
            secondary=Count('id', filter=Q(education='secondary')),
            higher=Count('id', filter=Q(education='higher')),
            academic_degree=Count('id', filter=Q(has_academic_degree=True)),
        )
        total = stats.pop('total')
        percent = {key: round(value * 100 / total, 1) if total else 0.0
                   for key, value in stats.items()}
        return Response({'total': total, 'count': stats, 'percent': percent})


# ============================================================
#                 Отчёт за месяц
# ============================================================

class MonthlyReportView(APIView):
    """
    Отчёт о работе библиотеки за месяц: ?year=2026&month=11

    - количество книг (экземпляров) и читателей на каждый день в каждом зале и в целом;
    - количество читателей, записавшихся за месяц, по залам и в целом.
    """

    def get(self, request):
        today = timezone.localdate()
        year = int_param(request, 'year', today.year)
        month = int_param(request, 'month', today.month)
        if not 1 <= month <= 12:
            return Response({'detail': 'month должен быть от 1 до 12'}, status=status.HTTP_400_BAD_REQUEST)

        rooms = list(ReadingRoom.objects.all())
        days_in_month = calendar.monthrange(year, month)[1]
        days = []

        for day_number in range(1, days_in_month + 1):
            d = date(year, month, day_number)
            on_day = Q(start_date__lte=d) & (Q(end_date__isnull=True) | Q(end_date__gte=d))

            books = dict(BookCopyRoomHistory.objects.filter(on_day)
                         .values_list('room').annotate(n=Count('book_copy', distinct=True)))
            readers = dict(ReaderRoomHistory.objects.filter(on_day)
                           .values_list('room').annotate(n=Count('reader', distinct=True)))
            rows = [{'room_id': r.id, 'room_number': r.room_number, 'room': r.name,
                     'books': books.get(r.id, 0), 'readers': readers.get(r.id, 0)}
                    for r in rooms]
            days.append({
                'date': d,
                'rooms': rows,
                'total': {
                    'books': BookCopyRoomHistory.objects.filter(on_day)
                    .aggregate(n=Count('book_copy', distinct=True))['n'],
                    'readers': ReaderRoomHistory.objects.filter(on_day)
                    .aggregate(n=Count('reader', distinct=True))['n'],
                },
            })

        registered = dict(ReaderRoomHistory.objects
                          .filter(start_date=F('reader__registration_date'),
                                  start_date__year=year, start_date__month=month)
                          .values_list('room').annotate(n=Count('reader', distinct=True)))
        registered_total = Reader.objects.filter(registration_date__year=year,
                                                 registration_date__month=month).count()

        return Response({
            'year': year,
            'month': month,
            'days': days,
            'registered': {
                'by_room': [{'room_id': r.id, 'room_number': r.room_number, 'room': r.name,
                             'count': registered.get(r.id, 0)} for r in rooms],
                'total': registered_total,
            },
        })
