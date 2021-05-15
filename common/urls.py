from django.urls import path,include
from common.views import RegisterAPIView

urlpatterns = [
   path('register',RegisterAPIView.as_view())
]