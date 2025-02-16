from django.urls import path
from fuel_stations import views

urlpatterns = [
    path('route/', views.find_route, name='find_route'),
]