from django.urls import path
from . import views

urlpatterns = [
    path("river-levels/", views.river_levels, name="river_levels")
]