from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='maps_index'),
    path('api/incidentes/', views.incidentes_api, name='incidentes_api'),
]
