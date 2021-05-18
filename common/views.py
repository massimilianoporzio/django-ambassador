from django.shortcuts import render

# Create your views here.
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
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

        data['is_ambassador'] = 'api/ambassador' in request.path #se chiamo url ambassador sono amabssador

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


        #Gestione dello scope per dire che sto usando un user che è di tipo ambassador / opp admin
        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'
        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized') # SE un ambassador USA le API di admin

        #PASSO LO SCOPE ALLA FUNZIONE CHE MI GENERA IL TOKEN DI AUTENTICAZIONE

        token = JWTAuthentication.generate_jwt(user.id,scope)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # serve che la classe che fa autenticazione metta il token

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data

        # if 'api/ambassador' in request.path:
        #     data['revenue'] = user.revenue

        return Response(data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, _):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)
