from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('avail-pdf/', views.avail_pdf,name='avail_pdf'),
    path('pdf/', views.pdf_viewer,name="pdf"),
]