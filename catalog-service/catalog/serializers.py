from rest_framework import serializers

from .models import Book, Category, Rating
from .service_clients import get_author_display, get_user_display


class CategorySerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source="id", read_only=True)
    label = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "value", "label"]


class RatingSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ["id", "user_id", "book", "review", "rate", "creation_date", "full_name"]

    def get_full_name(self, obj):
        return get_user_display(obj.user_id)


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    avg_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "name",
            "isbn",
            "front_img",
            "back_img",
            "description",
            "price",
            "language",
            "no_of_page",
            "year_of_publication",
            "total_number_of_book",
            "category",
            "category_name",
            "author_id",
            "author_name",
            "publisher_id",
            "publisher_name",
            "slug",
            "avg_rate",
        ]

    def get_author_name(self, obj):
        return get_author_display(obj.author_id)

    def get_publisher_name(self, obj):
        return get_user_display(obj.publisher_id)
