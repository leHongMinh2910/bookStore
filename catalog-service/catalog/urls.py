from django.urls import path

from .views import (
    BestRatedBooksView,
    BookDetailView,
    BookListCreateView,
    BookRatingsView,
    CategoryDetailView,
    CategoryListCreateView,
    PublisherBooksView,
    RatingListCreateView,
    RelatedBooksView,
    ReserveBookStockView,
    service_book_detail,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("books/", BookListCreateView.as_view(), name="book-list-create"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/service-detail/", service_book_detail, name="book-service-detail"),
    path("books/<int:pk>/reserve/", ReserveBookStockView.as_view(), name="book-reserve"),
    path("books/publisher/<int:publisher_id>/", PublisherBooksView.as_view(), name="publisher-books"),
    path("books/best-rated/", BestRatedBooksView.as_view(), name="best-rated-books"),
    path("books/<int:book_id>/related/", RelatedBooksView.as_view(), name="related-books"),
    path("ratings/", RatingListCreateView.as_view(), name="rating-list-create"),
    path("books/<int:book_id>/ratings/", BookRatingsView.as_view(), name="book-ratings"),
]
