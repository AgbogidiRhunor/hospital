from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('records/', include('records.urls')),
    path('lab/', include('lab.urls')),
    path('accounting/', include('accounting.urls')),
]
