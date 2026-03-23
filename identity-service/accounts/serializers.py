from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address, Author, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "phone",
            "profile_pic",
            "is_publisher",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PublisherSerializer(UserSerializer):
    certificate = serializers.CharField(required=False, allow_blank=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["certificate", "is_publisher"]

    def create(self, validated_data):
        validated_data["is_publisher"] = True
        return User.objects.create_user(**validated_data)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "biography", "publisher", "publisher_name"]

    def get_publisher_name(self, obj):
        return f"{obj.publisher.first_name} {obj.publisher.last_name}"


class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["id"] = self.user.id
        data["email"] = self.user.email
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name
        data["is_publisher"] = self.user.is_publisher
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["is_publisher"] = user.is_publisher
        return token
