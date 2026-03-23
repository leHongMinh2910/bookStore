from django.db.models import Avg
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, Category, Rating
from .serializers import BookSerializer, CategorySerializer, RatingSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.select_related("category").all().order_by("-id")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.select_related("category").all()
    serializer_class = BookSerializer


class PublisherBooksView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.filter(publisher_id=self.kwargs["publisher_id"]).select_related("category")


class BestRatedBooksView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.select_related("category").annotate(avg_rating=Avg("ratings__rate")).order_by("-avg_rating", "-id")[:4]


class RelatedBooksView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        book = Book.objects.get(pk=self.kwargs["book_id"])
        return Book.objects.filter(category=book.category).exclude(pk=book.pk).select_related("category")[:4]


class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.select_related("book").all().order_by("-id")
    serializer_class = RatingSerializer


class BookRatingsView(generics.ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(book_id=self.kwargs["book_id"]).select_related("book")


class ReserveBookStockView(APIView):
    def post(self, request, pk):
        book = Book.objects.get(pk=pk)
        quantity = int(request.data.get("quantity", 1))
        if quantity <= 0:
            return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity > book.total_number_of_book:
            return Response({"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)

        book.total_number_of_book -= quantity
        book.save(update_fields=["total_number_of_book"])
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def service_book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    serializer = BookSerializer(book)
    return Response(serializer.data)
