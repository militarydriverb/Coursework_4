from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('', views.home, name='home'),
]
