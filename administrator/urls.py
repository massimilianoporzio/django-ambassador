from django.urls import path,include

from .views import AmbassadorAPIView, ProductGenericAPIView, LinkAPIView, OrderAPIView,StatsAPIView
urlpatterns = [
   path('',include('common.urls')),
   path('ambassadors',AmbassadorAPIView.as_view()),
   path('products',ProductGenericAPIView.as_view()), #senza chiave primaria
   path('products/<str:pk>',ProductGenericAPIView.as_view()), #senza chiave primaria
   path('users/<str:pk>/links',LinkAPIView.as_view()), #GET i lINK associati all'user
   path('orders', OrderAPIView.as_view()), #ordini da processare
   path('users/<str:user_id>/stats',StatsAPIView.as_view()), #GET i STAS associati all'user


]