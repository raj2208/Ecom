from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from email.message import EmailMessage
import ssl
import smtplib
import hashlib
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup(request):
    if request.method=='POST':
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        if pass1 != pass2:
            messages.warning(request,"Passwords not matching")
        else:
            try:
                user = User.objects.get(email=email)
                messages.error(request,"user already exists")
            except:
                try:
                    user = User.objects.create_user(email,email,pass1)
                    user.is_active=False
                    user.save()
                    print("user created")
                    email_reciever=email
                    email_sender='Enter email here@gmail.com'
                    email_password='Enter password here'
                    subject='Hii This is a test email for SMTP gmail'
                    encryptemail=email+str(user.pk)+str(user.password)
                    print(encryptemail)
                    body="127.0.0.1:8000/auth/authenticate/"+email+"/"+hashlib.sha256(encryptemail.encode()).hexdigest()
                    print(body)
                    em=EmailMessage()
                    em['From']=email_sender
                    em['To']=email_reciever
                    em['Subject']=subject
                    em.set_content(body)
                    
                    context=ssl.create_default_context()
                    print("email configured")
                    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                        smtp.login(email_sender,email_password)
                        smtp.sendmail(email_sender,email_reciever,em.as_string())
                    messages.info(request,"Email Sent Please verify")
                except Exception as e:
                    user.delete()
                    print(e)
                    messages.warning(request,"Error occured")

    return render(request,"authentication/signup.html") 

def handleLogin(request):
    if request.method=="POST":
        username=request.POST['email']
        password=request.POST['pass1']
        myuser=authenticate(username=username,password=password)

        if myuser is not None:
            print("success")
            login(request,myuser)
            messages.success(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Wrong Credentials")
            return redirect('/auth/login')
    return render(request,"authentication/login.html") 

def handleLogout(request):
    logout(request)
    messages.success(request,"Logout Success")
    return redirect('/auth/login')

def handleAuthenticate(request,email,token):
    try:
        if User.objects.get(email=email):
            user=User.objects.get(email=email)
            if user.is_active is True:
                return HttpResponse("Already verified")
            encryptemail=str(user.email)+str(user.pk)+str(user.password)
            print(encryptemail)
            checktoken=hashlib.sha256(encryptemail.encode()).hexdigest()
            print(checktoken)
            print(token)
            if checktoken==token:
                user.is_active=True
                user.save()
                print(user.is_active)
                return HttpResponse("User authenticated")
            else:
                return HttpResponse("Mismatch")
    except Exception as e:
        print(e)
        return HttpResponse("Some error occured")