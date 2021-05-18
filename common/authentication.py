import jwt, datetime

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from app import settings
from core.models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        is_ambassador = 'api/ambassador' in request.path

        token = request.COOKIES.get('jwt')

        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('unauthenticated')

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope!')

        # ho controllato se quello che c'è nel token corrisponde alla request

        user = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        # if user.is_ambassador != is_ambassador:
        #     raise exceptions.AuthenticationFailed("Invalid scope!")

        return user, None

    @staticmethod
    def generate_jwt(id, scope):  # essendo static NON HA "self" come argomento
        payload = {
            'user_id': id,
            # 'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'scope': scope
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    # IN PRATICA nel token ci sono l'id utente, quando scade il token, quando è attivato e lo scope
