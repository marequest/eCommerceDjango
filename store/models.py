from django.db import models
from django.urls import reverse

from category.models import Category


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse("product_details", kwargs={"category_slug": self.category.slug, "product_slug": self.slug})

    def __str__(self):
        return self.name
