from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", view=views.signup, name="signup"),
    path("login/", view=views.login, name="login"),
    path("logout/", view=views.logout, name="logout"),
]