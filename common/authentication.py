import jwt, datetime

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from app import settings
from core.models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('unauthenticated')
        user = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        return user, None

    @staticmethod
    def generate_jwt(id): #essendo static NON HA "self" come argomento
        payload = {
            'user_id': id,
            # 'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
