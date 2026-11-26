from django.contrib import admin

from .models import (Author, Book, BookCopy, BookCopyRoomHistory, BookLoan,
                     Publisher, Reader, ReaderRoomHistory, ReadingRoom, Section)


@admin.register(ReadingRoom)
class ReadingRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'name', 'capacity')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'cipher', 'publisher', 'section', 'publication_year')
    search_fields = ('title', 'cipher')
    filter_horizontal = ('authors',)


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'book', 'current_room', 'status', 'received_date')
    list_filter = ('status', 'current_room')


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'full_name', 'current_room', 'education', 'status')
    list_filter = ('status', 'education', 'current_room')
    search_fields = ('full_name', 'ticket_number', 'passport_number')


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ('book_copy', 'reader', 'loan_date', 'return_date')


admin.site.register([Section, Publisher, Author, BookCopyRoomHistory, ReaderRoomHistory])
