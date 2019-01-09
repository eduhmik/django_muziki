# from django.contrib import admin
from django.urls import path
from .views import ListCreateSongsView, LoginView

urlpatterns = [
    path('songs/', ListCreateSongsView.as_view(), name="songs-all"),
    path('auth/login', LoginView.as_view(), name="auth-login")
]