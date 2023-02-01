"""Definiuje wzorce adresów URL dla aplikacji users."""

from django.urls import path, include

from . import views

app_name = 'users'
urlpatterns = [
    # Dołączenie domyślnych adresów URL uwierzytelniania
    path('', include('django.contrib.auth.urls')),
    # Strona rejestracyjna
    path('register/', views.register, name='register'),
]