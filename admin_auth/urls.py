from django.urls import path, include
from . import views

urlpatterns = [
    path("login/", view=views.login, name="login"),
    path("dashboard/", view=views.dashboard, name="dashboard"),
    path("list_pdfs/", view=views.list_pdfs, name="list_pdfs"),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path("signup-users/", view=views.signup_user, name="signup-users"),
]