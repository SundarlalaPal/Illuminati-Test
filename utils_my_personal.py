import pyrebase
import base64
import secrets
import string
import json
import os
from decouple import config
from datetime import datetime


class PDF_OPERATOR:

    def __init__(self):
        pass

    def encode_to_base64(self,binary_data):
        return base64.b64encode(binary_data).decode('utf-8')

    def decode_from_base64(self,base64_string):
        return base64.b64decode(base64_string)


class Firebase_Operations:

    def __init__(self):

        self.firebaseConfig = json.loads(config("FIREBASE_CONFIG"))

        self.firebase = pyrebase.initialize_app(self.firebaseConfig)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def create_user_actual(self,firstname, lastname, email, password,phone,age,guardianname,classs,board):
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.child("users").child(user_id).set({"First Name": firstname,"Last Name": lastname,"email": email,"Phone Number":phone,"Age":age,"Class":classs,"Guardian Name":guardianname,"Board":board,"created_at": timestamp})
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def create_user_tem(self,firstname, lastname, email, password,phone,age,guardianname,classs,board):
        try:
            s_users = self.db.child("signup_users").get()
            if s_users.each():
                for user in s_users.each():
                    if user.val().get("email") == email:
                        return False
            _users = self.db.child("users").get()
            if _users.each():
                for user_ in _users.each():
                    if user_.val().get("email") == email:
                        return False
            length = 10
            user_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
            self.db.child("signup_users").child(user_id).set({"user_id":user_id,"First Name": firstname,"Last Name": lastname,"email": email,"Password": password,"Phone Number":phone,"Age":age,"Class":classs,"Guardian Name":guardianname,"Board":board})
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def login_user(self,email, password):
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            print(user)
            _user = self.db.child("users").child(user['localId']).get().val()
            if _user is not None:
                print(_user)
                return user['localId']
            else:
                raise Exception("No user")
        except Exception as e:
            print(f"Error logging in: {e}")
            return None

    def get_user_data(self,user_id):
        try:
            user_data = self.db.child("users").child(user_id).get()
            return user_data.val()
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None

    def update_user_data(self,user_id, data):
        try:
            self.db.child("users").child(user_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating user data: {e}")
            return False

    def delete_user(self,user_id):
        try:
            self.db.child("users").child(user_id).remove()
            self.auth.delete_user_account(user_id)
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        
    def save_firebase_pdf(self,pdf_name,classs,value):
        self.db.child("pdfs").child(classs).child(pdf_name).set({"show":False,"name":pdf_name,"pdf_val":value})

    def retrive_firebase_pdf(self,pdf_name,classs):
        data = self.db.child("pdfs").child(classs).child(pdf_name).get().val().get("pdf_val")
        return PDF_OPERATOR().decode_from_base64(data)
    
    def check_signup_user(self,email):
        d = self.db.child("signup_users").get()
        if d.each():
            for m in d.each():
                if m.val().get("email") == email:
                    return False
        b = self.db.child("users").get()
        if b.each():
            for n in b.each():
                if n.val().get("email") == email:
                    return False
        return True
