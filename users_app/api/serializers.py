from rest_framework import serializers

from users_app.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'password',
            'email',
            'balance',
        ]
