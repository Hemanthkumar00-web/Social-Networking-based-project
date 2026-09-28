from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import ForgotPasswordForm, LoginForm, RegisterForm, SetNewPasswordForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        return render(request, 'authentication/register.html', {'form': form})

    form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('feed')
            form.add_error(None, 'Invalid username or password.')
        return render(request, 'authentication/login.html', {'form': form})

    form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
            send_mail(
                'Reset your Instagram password',
                render_to_string('authentication/reset_email.txt', {
                    'user': user,
                    'reset_url': reset_url,
                }),
                'noreply@instagram.com',
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_sent')
        return render(request, 'authentication/forgot_password.html', {'form': form})
    form = ForgotPasswordForm()
    return render(request, 'authentication/forgot_password.html', {'form': form})


def password_reset_sent(request):
    return render(request, 'authentication/password_reset_sent.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'authentication/reset_password_invalid.html')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, 'Password has been reset successfully! You can now log in.')
            return redirect('login')
        return render(request, 'authentication/reset_password.html', {'form': form})

    form = SetNewPasswordForm()
    return render(request, 'authentication/reset_password.html', {'form': form})
