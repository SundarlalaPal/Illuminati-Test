from django.shortcuts import render,redirect
import base64
import pyrebase
import utils_my_personal
import json
import os


# Create your views here.
from decouple import config
firebaseConfig = json.loads(config("FIREBASE_CONFIG"))

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Create your views here.
def pdf_viewer(request):
    if request.method == "GET":
        if "name_pdf" not in request.session or "allow_pdf" not in request.session:
            return redirect("/")
        if "id_token" not in request.session:
            return redirect("/")
        
        user_data = utils_my_personal.Firebase_Operations().get_user_data(request.session["id_token"])
        classs = user_data.get('Class')
        name = request.session["name_pdf"]
        pdf_data = utils_my_personal.Firebase_Operations().retrive_firebase_pdf(name,classs)
        # pdf_path = f'pdfs_storage\{name}.pdf' 
        # Ensure this file exists in the correct location
        
        # with open(pdf_path, "rb") as f:
        #     binary_data = f.read()
        
        # Convert PDF to base64
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        
        context = {'pdf_content': base64_pdf}
        return render(request, 'students/pdf.html', context)
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            allow = data.get("is_okk")
            if allow == True:
                del request.session['name_pdf']
                del request.session['allow_pdf']
                return redirect()
        except Exception as e:
            return redirect("/students/avail-pdf/")

def avail_pdf(request):
    if "id_token" not in request.session:
        return redirect("/")
    if request.method == "GET":
        pdfs = []
        classs = utils_my_personal.Firebase_Operations().get_user_data(request.session["id_token"]).get('Class')
        # classs = 5
        pdfss = db.child("pdfs").child(classs).get()
        if pdfss.each():
            for pd in pdfss.each():
                if pd.val().get("show") == True or pd.val().get("show") == "True":
                    pdfs.append({"name":pd.val().get("name")})
        
        return render(request, "students/me_select.html",{"pdfs":pdfs})
    
    if request.method == "POST":
        data = json.loads(request.body)

        pdf_data = {
            "allow": data.get("open_ok"),
            "name": data.get("name__"),
        }

        if pdf_data["allow"] == "True" or pdf_data["allow"] == True:
            request.session["allow_pdf"] = True
            request.session["name_pdf"] = pdf_data["name"]
            return redirect("/students/pdf/")
        
        return redirect("/")
