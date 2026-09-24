from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('predict_flood/', views.predict_flood, name='predict_flood'),
]