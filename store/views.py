from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from store.models import Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


# Create your views here.
def store(request, slug=None):
    categories = None
    products = None

    if slug is not None:
        categories = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count
    }

    return render(request, 'store/store.html', context)


def product_details(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'product': single_product,
        'in_cart': in_cart
    }

    return render(request, 'store/product_details.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_at').filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
            product_count = products.count()

    context = {
        'keyword': keyword,
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)