from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Address, Author, User
from .serializers import AddressSerializer, AuthorSerializer, CustomTokenSerializer, PublisherSerializer, UserSerializer


class IsPublisherUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_publisher)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(is_publisher=False)
    serializer_class = UserSerializer


class PublisherRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(is_publisher=True)
    serializer_class = PublisherSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_publisher=False)
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PublisherListView(generics.ListAPIView):
    queryset = User.objects.filter(is_publisher=True)
    serializer_class = PublisherSerializer


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Address.objects.filter(user_id=user_id)


class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
