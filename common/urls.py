from django.urls import path,include
from common.views import (
   RegisterAPIView, LoginAPIView, LogoutAPIView,
   UserAPIView,ProfileInfoAPIView,ProfilePasswordAPIView
)


urlpatterns = [
   path('register',RegisterAPIView.as_view()),
   path('login',LoginAPIView.as_view()),
   path('logout',LogoutAPIView.as_view()),
   path('user',UserAPIView.as_view()),
   path('user/update',ProfileInfoAPIView.as_view()),
   path('user/password',ProfilePasswordAPIView.as_view()),
]