from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponseRedirect

urlpatterns = [
    path("", include("blog.urls")),
    path("admin/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('seller', lambda request: HttpResponseRedirect('/seller/')),  # /seller를 /seller/로 리다이렉트
    path('seller/', include("seller.urls")),
    path('cart/', include('cart.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
