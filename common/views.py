from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterAPIView(APIView):
    def post(self,request):
        print('UFFA')
        return Response('Hello')
