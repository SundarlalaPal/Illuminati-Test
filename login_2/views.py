from django.shortcuts import render, redirect
import utils_my_personal
import base64
import os

def index(request):
    return render(request,"index.html")

def dashboard(request):
    if "id_token" not in request.session:
        return redirect("/auth/login")
    user_data = utils_my_personal.Firebase_Operations().get_user_data(request.session["id_token"])
    context = {
        "First_Name": user_data.get('First Name'),
         "Last_Name": user_data.get('Last Name'),
         "email": user_data.get('email')
    }
    return render(request, "dashboard.html", context)

def coming_soon(request):
    return render(request,"coming_soon.html") 
