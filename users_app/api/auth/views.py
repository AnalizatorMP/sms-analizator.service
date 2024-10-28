import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.db import IntegrityError
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.api.serializers import UserSerializer
from users_app.models import User


def authenticate_custom(request, email=None, password=None, **kwargs):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    if user.check_password(password):
        return user


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password'],
        ),
        responses={
            200: 'Успешный вход',
            401: 'Неверный логин или пароль',
        },
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate_custom(request, email=email, password=password)
        # print(user)
        # print(type(user))

        if user:
            if not user.is_active:
                return Response({'error': 'Email еще не подтвержден'}, status=status.HTTP_401_UNAUTHORIZED)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id})
        else:
            return Response({'error': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: 'Успешный выход',
        },
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'success': True})


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            },
            required=['email', 'password'],
        ),
        responses={
            201: 'Пользователь успешно зарегистрирован',
            400: 'Некорректные данные регистрации',
        },
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()

            return Response({'success': True, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
