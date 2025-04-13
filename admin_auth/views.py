from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import pyrebase
import json
import utils_my_personal
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import base64


from decouple import config
firebaseConfig = json.loads(config("FIREBASE_CONFIG"))

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def get_admin_data(name):
    return db.child("superusers").child(f"{name}").get().val()

def chech_auth_admin(email,passw):
    data = db.child("superusers").get().val()
    for datas in data:
        val = db.child("superusers").child(f"{datas}").get().val().get("email")
        pas = db.child("superusers").child(f"{datas}").get().val().get("password")
        if val == email and pas == passw:
            return datas
    return False

def login(request):
    if request.method == "GET":
        if "name" not in request.session:
            return render(request, "admin_auth/login.html")
        return redirect("/admin-auth/dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        login_user_id = chech_auth_admin(email, password)
        if login_user_id != False:
            request.session["name"] = login_user_id
            return redirect("/admin-auth/dashboard")
        else:
            return render(request, "admin_auth/login.html", {"error": "Invalid credentials"})

def dashboard(request):
    if "name" not in request.session:
        return redirect("/admin-auth/login/") 
    user_data = get_admin_data(request.session["name"])
    context = {
        "First_Name": user_data.get('First Name'),
         "email": user_data.get('email')
    }
    return render(request, "admin_auth/dashboard.html", context)

def signup_user(request):
    if request.method == "GET":
        users = []
        signup_users = db.child("signup_users").get()
        if signup_users.each():
            for sg_u in signup_users.each():
                # if pd.val().get("show") == True:
                users.append({"user_id":sg_u.val().get("user_id"),"First_Name": sg_u.val().get("First Name"),"Last_Name": sg_u.val().get("Last Name"),"email": sg_u.val().get("email"),"Password": sg_u.val().get("Password"),"Phone_Number":sg_u.val().get("Phone Number"),"Age":sg_u.val().get("Age"),"Class":sg_u.val().get("Class"),"Guardian_Name":sg_u.val().get("Guardian Name"),"Board":sg_u.val().get("Board")})
        # print(users)
        return render(request,"admin_auth/list_signup.html",{"users":users})
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from request
            
            # Extracting all fields
            user_data = {
                "user_id": data.get("user_id"),
                "First Name": data.get("First_Name"),
                "Last Name": data.get("Last_Name"),
                "email": data.get("email"),
                "Password": data.get("Password"),
                "Phone Number": data.get("Phone_Number"),
                "Age": data.get("Age"),
                "Class": data.get("Class"),
                "Guardian Name": data.get("Guardian_Name"),
                "Board": data.get("Board"),
                "Allow": data.get("Allow")  # This will be True/False from button click
            }

            # Update Firebase (or save data as needed)
            if user_data["Allow"] == True or user_data["Allow"] == "True":
                d = utils_my_personal.Firebase_Operations().create_user_actual(user_data["First Name"],user_data["Last Name"],user_data["email"],user_data["Password"],user_data["Phone Number"],user_data["Age"],user_data["Guardian Name"],user_data["Class"],user_data["Board"])
                # db.child("users").child(user_data["uid"]).set(user_data)
                db.child("signup_users").child(user_data["user_id"]).remove()
                
            else:
                db.child("signup_users").child(user_data["user_id"]).remove()
            
            return redirect("/admin-auth/signup-users")

        except Exception as e:
            return redirect("/admin-auth/signup-users")

def list_pdfs(request):
    pdfs_val_true = []
    pdfs_val_false = []
    if request.method == "GET":
        for i in range(5,13):
            pdfss = db.child("pdfs").child(i).get()
            if pdfss.each():
                for pd in pdfss.each():
                    if pd.val().get("show") == True or pd.val().get("show") == "True":
                        pdfs_val_true.append({"Class":i,"name":pd.val().get("name")})
                    else:
                        pdfs_val_false.append({"Class":i,"name":pd.val().get("name")})
        return render(request, "admin_auth/list_pdfs.html",{"t_pdfs":pdfs_val_true,"f_pdfs":pdfs_val_false})
    
    if request.method == "POST":
        data = json.loads(request.body)

        pdf_data = {
            "allow": data.get("open_ok"),
            "name": data.get("name__"),
            "class": data.get("class"),
        }

        if pdf_data["allow"] == True or pdf_data["allow"] == "True":
            db.child("pdfs").child(pdf_data["class"]).child(pdf_data["name"]).update({"show":True})
        elif pdf_data["allow"] == False or pdf_data["allow"] == "False":
            db.child("pdfs").child(pdf_data["class"]).child(pdf_data["name"]).update({"show":False})
        elif pdf_data["allow"] == "delete":
            db.child("pdfs").child(pdf_data["class"]).child(pdf_data["name"]).remove()

        return redirect("/admin-auth/list_pdfs/")


def upload_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        selected_class = request.POST.get('class')

        # Check if both file and class are provided
        if not pdf_file or not selected_class:
            return render(request, 'admin_auth/upload.html', {'message': 'Please select a class and upload a file.'})

        # Validate that the selected class is valid (between 5 and 12)
        valid_classes = [str(i) for i in range(5, 13)]
        if selected_class not in valid_classes:
            return render(request, 'admin_auth/upload.html', {'message': 'Invalid class selected.'})

        # Build the folder path: media/uploaded_pdf/class_X/
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_pdf', f'class_{selected_class}')
        os.makedirs(upload_dir, exist_ok=True)  # Create folder if not exists

        # Save the file using FileSystemStorage
        fs = FileSystemStorage(location=upload_dir)
        fs.save(pdf_file.name, pdf_file)

        file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_pdf', f'class_{selected_class}', pdf_file.name)

        with open(file_path, "rb") as f:
            binary_data = f.read()
        
        base64_pdf_data = base64.b64encode(binary_data).decode('utf-8')
        file_name, file_extension = os.path.splitext(pdf_file.name)

        utils_my_personal.Firebase_Operations().save_firebase_pdf(file_name,selected_class,base64_pdf_data) 

        os.remove(file_path)


        return render(request, "admin_auth/upload.html", {'message': f'Upload successful for Class {selected_class}!'})

    # For GET requests, simply show the upload form
    return render(request, "admin_auth/upload.html")  
