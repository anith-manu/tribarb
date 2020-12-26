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
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from authentication.models import Shop

import random 
import threading

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class RegistrationView(View):    

    def generateUsername(self, firstName, lastName):
        first_letter = firstName[0].lower()
        three_letters_surname = lastName[:3].lower()
        number = '{:03d}'.format(random.randrange(1, 999))
        username = (first_letter + three_letters_surname + number)
        return username

    def get(self, request):
        shop_form = ShopForm()
        return render(request, 'auth/register.html', {
		"shop_form" : shop_form,
        "mapsKey" : settings.GOOGLE_MAPS_API_KEY
		})

    def post(self, request):
        shop_form = ShopForm(request.POST, request.FILES)
        context={
            'data':request.POST,
            'has_error':False,
            'shop_form':shop_form,
            "mapsKey" : settings.GOOGLE_MAPS_API_KEY
        }

        fName=request.POST.get('first_name')
        lName=request.POST.get('last_name')
        email=request.POST.get('email')
        password=request.POST.get('password')


        if not validate_email(email):
            messages.add_message(request, messages.ERROR, 'Please provide a valid email.')
            context['has_error']=True

        if len(password)<6:
            messages.add_message(request, messages.ERROR, 'Password should be at least 6 characters long.')
            context['has_error']=True
        
        if len(fName)==0:
            messages.add_message(request, messages.ERROR, 'Please provide your first name.')
            context['has_error']=True
        
        if len(lName)==0:
            messages.add_message(request, messages.ERROR, 'Please provide your last name.')
            context['has_error']=True
    
        
        
        try:
            if User.objects.get(email=email):
                
                user = User.objects.get(email=email)
                if user.is_active == False:
                    user.delete()
                    
                else :
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


        if not shop_form.is_valid():
            messages.add_message(request, messages.ERROR, 'Please provide all the shop info.')
            context['has_error']=True
        
        if request.POST.get("shop_bookings") == None and request.POST.get("home_bookings") == None:
            messages.add_message(request, messages.ERROR, 'Please select the accepted booking type(s).')
            context['has_error']=True
        

       
     
        if context['has_error']:
            return render(request, 'auth/register.html', context, status=400)
        else:
            # Create User
            username = self.generateUsername(fName, lName)
            user = User.objects.create(username=username,email=email, first_name=fName, last_name=lName, is_active=False)
            user.set_password(password)
            user.save()

            # Create Shop
            new_shop = shop_form.save(commit=False)
            new_shop.user = user
            new_shop.save()

    

        ##### Send Activation Email #####

        current_site = get_current_site(request)
        email_subject = 'Activate Your Tribarb Shop Manager Account'

        context = ({
            'user':user,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)       
        })


        text_content = render_to_string('auth/activate.txt', context)
        html_content = render_to_string('auth/activate.html', context)

        try:
            emailMessage = EmailMultiAlternatives(subject=email_subject, body=text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
            emailMessage.attach_alternative(html_content, "text/html")
            emailMessage.send(fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR, 'There was an error while sending the activation email. Please try to re-register.')
            return render(request, 'auth/register.html', context, status=400)

        return render(request, 'auth/email-sent.html')





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
            messages.add_message(request, messages.SUCCESS, 'Account activated! You can now login.')
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
            email_subject = 'Tribarb Shop Manager Password Reset'
            context = ({
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
                'email' : email      
            })


            text_content = render_to_string('auth/reset-user-password.txt', context)
            html_content = render_to_string('auth/reset-user-password.html', context)

            try:
                emailMessage = EmailMultiAlternatives(subject=email_subject, body=text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
                emailMessage.attach_alternative(html_content, "text/html")
                emailMessage.send(fail_silently=False)
                messages.success(request, 'Please check your email for a link to reset your password.')
            except:
                messages.add_message(request, messages.ERROR, 'There was an error while sending the password reset email. Please try again.')
        
        else:
            messages.error(request, 'An account associated with this email does not exist.')
            return render(request, 'auth/request-reset-email.html')


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
    