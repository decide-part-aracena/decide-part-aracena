from .forms import NewUserForm, LoginUserForm
from django.contrib.auth import login, authenticate, logout
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from decide.settings import BASEURL
from .serializers import UserSerializer
from django.core.cache import cache
from .forms import MagicLinkForm
from django.views.decorators.http import require_http_methods
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.core.mail import send_mail
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
import secrets

URL_BASE = "/base/"


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})
    

class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)


def RegisterUserView(request):
    if request.user.is_authenticated and not(request.user.is_staff):
        return redirect(URL_BASE)

    if request.method == "POST":
        form = NewUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=True)
            user.save()
            return redirect(URL_BASE)
        return render(request=request, template_name="authentication/register.html", context={"register_form": form})
    else:
        form = NewUserForm()
        return render(request=request, template_name="authentication/register.html", context={"register_form": form})


def LoginUserView(request):
    if request.user.is_authenticated:
        return redirect(URL_BASE)

    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(URL_BASE)
    form = LoginUserForm()
    return render(request=request, template_name="authentication/login.html", context={"login_form": form})


def LogoutUserView(request):
    logout(request)
    return redirect(URL_BASE)


@require_http_methods(["GET", "POST"])
def magic_link_via_email(request: HttpRequest):
    '''
    Generate a 10 minutes magic link and send it via email to registered users
    '''
    timeout = 10*60  # minutes
    if request.user.is_authenticated:
        return redirect(URL_BASE)

    if request.POST:
        form = MagicLinkForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                token = secrets.token_urlsafe(nbytes=16)
                link = f"{BASEURL}/authentication/magic-link/{token}"
                cache.get_or_set(token, email, timeout=timeout)
                send_mail(
                    subject="Decide - Login magic link",
                    message=f"Copy in the browser the following link in order to login {link}",
                    from_email='decide.part.aracena@outlook.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
    return render(request, "authentication/magic_auth.html")


@require_http_methods("GET")
def authenticate_via_magic_link(request: HttpRequest, token: str):
    '''
    Use the magic link(token) to log in the user
    '''
    email = cache.get(token)
    if email is None:
        return HttpResponseBadRequest(content="Link has expired, request a new one")
    cache.delete(token)
    user = User.objects.get(email=email)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect(URL_BASE)
