from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome, name='home'),
    path('date', views.date, name='date'),
    path('about', views.about, name='about')]
