from django.shortcuts import render

# Create your views here.
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from administrator.serializers import ProductSerializer
from common.authentication import JWTAuthentication
from common.serializers import UserSerializer
from core.models import User, Product


class AmbassadorAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _):
        ambassadors = User.objects.filter(is_ambassador=True)
        serializer = UserSerializer(ambassadors, many=True) #many perché potrebbe restituire più di un oggetto
        return Response(serializer.data)

class ProductGenericAPIView(generics.GenericAPIView,mixins.RetrieveModelMixin,mixins.CreateModelMixin,
                            mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin): #generics : con operazioni "std" (get_queryset...etc)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk: #DETAIL (ho l'id nella GET)
            return self.retrieve(request, pk) #retrive da RetrieveModelMixin

        return self.list(request) # LISTA list da ListModelMixin

    def post(self, request):
        response = self.create(request)
        return response

    def put(self, request, pk=None):
        response = self.partial_update(request, pk) #like a PATCH (DRF non supporta PATCH)
        return response

    def delete(self, request, pk=None):
        response = self.destroy(request, pk)
        return response

