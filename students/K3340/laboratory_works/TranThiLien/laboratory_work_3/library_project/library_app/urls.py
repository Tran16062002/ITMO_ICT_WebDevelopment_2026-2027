from django.urls import path

from . import views

app_name = 'library_app'

urlpatterns = [
    # --- CRUD: справочники ---
    path('rooms/', views.ReadingRoomListCreateView.as_view()),
    path('rooms/<int:pk>/', views.ReadingRoomDetailView.as_view()),
    path('sections/', views.SectionListCreateView.as_view()),
    path('sections/<int:pk>/', views.SectionDetailView.as_view()),
    path('publishers/', views.PublisherListCreateView.as_view()),
    path('publishers/<int:pk>/', views.PublisherDetailView.as_view()),
    path('authors/', views.AuthorListCreateView.as_view()),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view()),

    # --- CRUD: книги, экземпляры, читатели, выдачи ---
    path('books/', views.BookListCreateView.as_view()),
    path('books/<int:pk>/', views.BookDetailView.as_view()),
    path('copies/', views.BookCopyListCreateView.as_view()),
    path('copies/<int:pk>/', views.BookCopyDetailView.as_view()),
    path('readers/', views.ReaderListCreateView.as_view()),
    path('readers/<int:pk>/', views.ReaderDetailView.as_view()),
    path('loans/', views.BookLoanListCreateView.as_view()),
    path('loans/<int:pk>/', views.BookLoanDetailView.as_view()),

    # --- GET с вложенными объектами ---
    path('rooms/<int:pk>/readers/', views.ReadingRoomReadersView.as_view()),
    path('books/<int:pk>/full/', views.BookFullView.as_view()),
    path('authors/<int:pk>/books/', views.AuthorBooksView.as_view()),
    path('readers/<int:pk>/books/', views.ReaderBooksView.as_view()),
    path('copies/<int:pk>/history/', views.BookCopyHistoryView.as_view()),
    path('readers/<int:pk>/history/', views.ReaderHistoryView.as_view()),

    # --- Операции библиотекаря ---
    path('copies/<int:pk>/move/', views.BookCopyMoveView.as_view()),
    path('copies/<int:pk>/write-off/', views.BookCopyWriteOffView.as_view()),
    path('readers/<int:pk>/move/', views.ReaderMoveView.as_view()),
    path('readers/<int:pk>/reregister/', views.ReaderReregisterView.as_view()),
    path('readers/exclude-expired/', views.ExcludeExpiredReadersView.as_view()),

    # --- Аналитика и отчёт ---
    path('analytics/overdue-readers/', views.OverdueReadersView.as_view()),
    path('analytics/rare-book-readers/', views.RareBookReadersView.as_view()),
    path('analytics/young-readers/', views.YoungReadersView.as_view()),
    path('analytics/education/', views.EducationStatsView.as_view()),
    path('reports/monthly/', views.MonthlyReportView.as_view()),
]
