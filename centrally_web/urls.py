from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('maps/', include('maps.urls')),
    path('analytics/', include('analytics.urls')),
]
