from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from authentication.forms import ShopForm


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

# Create your views here.

import threading

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class RegistrationView(View):
    shop_form = ShopForm()

    def get(self, request):
        shop_form = ShopForm()
        return render(request, 'auth/register.html', {
		"shop_form": shop_form 
		})

    def post(self, request):
        context={
            'data':request.POST,
            'has_error':False
        }

        email=request.POST.get('email')
        username=request.POST.get('username')
        fName=request.POST.get('first_name')
        lName=request.POST.get('last_name')
        password=request.POST.get('password')
        password2=request.POST.get('password2')

        if not validate_email(email):
            messages.add_message(request, messages.ERROR, 'Please provide a valid email.')
            context['has_error']=True

        if len(password)<6:
            messages.add_message(request, messages.ERROR, 'Password should be at least 6 characters long.')
            context['has_error']=True

        if password!=password2:
            messages.add_message(request, messages.ERROR, 'Passwords don\'t match.')
            context['has_error']=True
        
        try:
            if User.objects.get(email=email):
                messages.add_message(request, messages.ERROR, 'Email is already taken.')
                context['has_error']=True
        except Exception:
            pass
      
        try:
            if User.objects.get(username=username):
                messages.add_message(request, messages.ERROR, 'Username is already taken.')
                context['has_error']=True
        except Exception:
            pass
        
     
        if context['has_error']:
            return render(request, 'auth/register.html', context, status=400)

        user = User.objects.create(username=username,email=email)
        user.set_password(password)
        user.first_name=fName
        user.last_name=lName
        user.is_active=False

        user.save()

        #####
        shop_form = ShopForm(request.POST, request.FILES)

        if shop_form.is_valid():
            new_shop = shop_form.save(commit=False)
            new_shop.user = user
            new_shop.save()
        else:
            return render(request, 'auth/register.html', context, status=400)
        #####

        current_site = get_current_site(request)
        email_subject = 'Activate Your Tribarb Account'
        message = render_to_string('auth/activate.html', 
        {
            'user':user,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)       
        }
        )

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email], 
        )

        EmailThread(email_message).start()
        messages.add_message(request, messages.SUCCESS, 'Account created successfully! Please check your email for a verification link.')

        return redirect('login')



class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')
    
    def post(self, request):
        context={
            'data': request.POST,
            'has_error': False
        }
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        if username == '':
             messages.add_message(request, messages.ERROR, 'Username is required.')
             context['has_error']=True
        if password == '':
             messages.add_message(request, messages.ERROR, 'Password is required.')
             context['has_error']=True
        
        user=authenticate(request, username=username, password=password)

        if not user and not context['has_error']:
            messages.add_message(request, messages.ERROR, 'Invalid login credentials.')
            context['has_error']=True
        
        if context['has_error']:
            return render(request, 'auth/login.html', status=401, context=context)
        
        login(request,user)
        return redirect('shop-bookings')



class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user=None

        if user is not None and generate_token.check_token(user, token):
            user.is_active=True
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Account activated successfully!')
            return redirect('login')
        
        return render(request, 'auth/activate_failed.html', status=401)



class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Logged out successfully.')
        return redirect('login')



class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'auth/request-reset-email.html')

    def post(self, request):
        email = request.POST['email']

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email.')
            return render(request, 'auth/request-reset-email.html')

        user = User.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset your Password]'
            message = render_to_string('auth/reset-user-password.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            EmailThread(email_message).start()

        messages.success(request, 'Thanks! Please check your email for a link to reset your password.')
        return render(request, 'auth/request-reset-email.html') 


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Password reset link is invalid. Please request a new one.')
                return render(request, 'auth/request-reset-email.html')

        except DjangoUnicodeDecodeError:
            messages.success(request, 'Invalid link.')
            return render(request, 'auth/request-reset-email.html')

        return render(request, 'auth/set-new-password.html', context)
    

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR, 'Password should be at least 6 characters long.')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR, 'Passwords don\'t match.')
            context['has_error'] = True

        if context['has_error'] == True:
            return render(request, 'auth/set-new-password.html', context)
        
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password has been reset. You can now login with your new password.')

            return redirect('login')

        except DjangoUnicodeDecodeError:
            messages.error(request, 'Something went wrong')
            return render(request, 'auth/set-new-password.html', context)

        return render(request, 'auth/set-new-password.html', context)