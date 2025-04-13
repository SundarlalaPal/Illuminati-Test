from django.shortcuts import render, redirect
import utils_my_personal

# Create your views here.
def signup(request):
    if request.method == "POST":
        try:
            first_name = str(request.POST.get("firstname")).strip()
            last_name = str(request.POST.get("lastname")).strip()
            age = request.POST.get("age")
            guardianname = str(request.POST.get("guardianname")).strip()
            phonenumber = request.POST.get("phonenumber")
            email = str(request.POST.get("email")).strip()
            password = str(request.POST.get("password")).strip()
            classs = request.POST.get("class")
            board = str(request.POST.get("board")).strip()
            is_applicable = utils_my_personal.Firebase_Operations().check_signup_user(email)
            if is_applicable:
                id_token = utils_my_personal.Firebase_Operations().create_user_tem(firstname=first_name,lastname=last_name,email=email, password=password,age=age,guardianname=guardianname,phone=phonenumber,classs = classs, board=board)
                if id_token==False:
                    return render(request, "authentication/signup.html", {"error": "User already exists"})
                else:
                    return render(request, "authentication/signedup.html")
            else:
                return render(request, "authentication/signup.html", {"error": "User already exists"})
        except Exception as e:
            return redirect("/")
    if request.method == "GET":
        return render(request, "authentication/signup.html")

def login(request):
    if request.method == "GET":
        return render(request, "authentication/login.html")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        login_user_id = utils_my_personal.Firebase_Operations().login_user(email, password)
        if login_user_id:
            request.session["id_token"] = login_user_id
            return redirect("/dashboard")
        else:
            return render(request, "authentication/login.html", {"error": "Invalid credentials"})



def logout(request):
    request.session.flush()  # Clears session
    return redirect("/")
            
