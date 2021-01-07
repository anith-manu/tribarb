from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('shop/register', views.RegistrationView.as_view(), name='register'),
    path('shop/login', views.LoginView.as_view(), name='login'),
    path('shop/logout', views.LogoutView.as_view(), name='logout'),
    path('shop/activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('shop/request-reset-email', views.RequestResetEmailView.as_view(), name='request-reset-email'),
    path('shop/set-new-password/<uidb64>/<token>', views.SetNewPasswordView.as_view(), name='set-new-password')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
