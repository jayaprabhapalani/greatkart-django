from django.contrib import messages,auth
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib.auth.decorators import login_required
#verfication email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# Create your views here.

def register(request):
    #handling submission
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            #creating username from email
            username=email.split('@')[0]
           
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,password=password,email=email)
            user.phone_number=phone_number # not in create user(from account manager) so manually creating here
            user.save()
            
            #uUSER ACTIVATION
            current_site=get_current_site(request)
            mail_subject='Please activate your account'
            message=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
                
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            
            #for messages
            #messages.success(request,'Thank You for registering with us. We have sent you a verfication email to your email address. Please very it .')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:    
        form=RegistrationForm()
    context={
        'form':form,
        }
    return render(request,'accounts/register.html',context)



def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        
        user=auth.authenticate(email=email,password=password)
        
        if user is not None:
            auth.login(request,user)
            messages.success(request,"You are logged in")
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')


#u can only logout the sys when ur logged in
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')
    
    
#actiavte
def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"Congratulations! Your account is activated.")
        return redirect('login')
        
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')        
            
            
#u can only logout the sys when ur logged in
@login_required(login_url='login')  
def dashboard(request):
    return render(request,'accounts/dashboard.html')  

    
def forgotPassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email=email)
            #Reset password email
            current_site=get_current_site(request)
            mail_subject='Please Reset your password'
            message=render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
                
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            
            #for messages
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')
            
            
            
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')   


def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset yout password')
        return redirect('resetPassword')
    else:
        messages.error(request,"This link has been expired")    
        return redirect('login')
    
#reset password
def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confrim_password=request.POST['confirm_password']
        if password==confrim_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")  
            return redirect('login')          
        else:
            messages.error(request,"Password does not match")    
            return redirect('resetPassword')
    else:    
        return render(request,'accounts/resetPassword.html')
    