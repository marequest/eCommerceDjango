"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

import portfolio.views
from . import views, settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from portfolio import views as portfolio_views


urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('adminsl/', admin.site.urls),
    # TODO #################### Vrati sve ovo
    # path('', views.home, name='home'),
    # path('store/', include('store.urls')),
    # path('cart/', include('carts.urls')),
    # path('accounts/', include('accounts.urls')),
    # path('orders/', include('orders.urls')),
    path('portfolio/', portfolio_views.portfolio_page, name='portfolio_page'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# Redirect all other URLs to the portfolio view
urlpatterns += [
    re_path(r'^.*$', portfolio_views.portfolio_page, name='redirect_to_portfolio'),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns + staticfiles_urlpatterns()