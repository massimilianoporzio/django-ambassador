from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'is_ambassador']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data): #quando si chiede un POST o PUT / INSERT il metodo create salva su db
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

