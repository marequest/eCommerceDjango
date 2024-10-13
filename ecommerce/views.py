from django.http import HttpResponse
from django.shortcuts import render

from store.models import Product, ReviewRating


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_at')
    reviews = []

    # Get reviews
    if products is not None:
        for product in products:
            reviews = ReviewRating.objects.filter(product_id=product.id, status=True).order_by('id')
    else:
        products = []

    context = {
        'products': products,
        'reviews': reviews
    }
    return render(request, 'home.html', context)