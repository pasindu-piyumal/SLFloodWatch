from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('locations/', views.locations, name='locations'),
    path('locations/<int:pk>/', views.location_detail, name='location_detail')
]