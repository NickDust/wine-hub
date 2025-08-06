from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="Register"),
    path("logs/", views.LogView.as_view(), name="logs")
]
