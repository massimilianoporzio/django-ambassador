from django.shortcuts import render

# Create your views here.
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from common.serializers import UserSerializer
from core.models import User
from .authentication import JWTAuthentication


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        data['is_ambassador'] = 0

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        try:
            user = User.objects.get(email=email)
        except:
            raise exceptions.AuthenticationFailed('User not found!')
        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect Password!')

        jwt_authentication = JWTAuthentication()
        token = jwt_authentication.generate_jwt(user.id)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'success'
        }

        return response
