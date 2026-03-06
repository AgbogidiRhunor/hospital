from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def healthz(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('healthz', healthz),
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('records/', include('records.urls')),
    path('lab/', include('lab.urls')),
    path('accounting/', include('accounting.urls')),
]