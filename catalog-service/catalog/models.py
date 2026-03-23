from django.db import models
from django.db.models import Avg
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    LANGUAGE_CHOICES = (
        ("Arabic", "Arabic"),
        ("English", "English"),
    )

    name = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, unique=True)
    front_img = models.TextField(blank=True)
    back_img = models.TextField(blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    no_of_page = models.IntegerField(null=True, blank=True)
    year_of_publication = models.DateField()
    total_number_of_book = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="books")
    author_id = models.IntegerField()
    publisher_id = models.IntegerField()
    slug = models.SlugField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def avg_rate(self):
        avg = self.ratings.aggregate(avg_value=Avg("rate"))
        return round(avg["avg_value"], 2) if avg["avg_value"] else 0

    def __str__(self):
        return self.name


class Rating(models.Model):
    user_id = models.IntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    review = models.TextField(blank=True)
    rate = models.PositiveIntegerField()
    creation_date = models.DateField(auto_now_add=True)
