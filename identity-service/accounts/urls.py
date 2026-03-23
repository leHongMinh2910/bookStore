from django.urls import path

from .views import (
    AddressListCreateView,
    AuthorDetailView,
    AuthorListCreateView,
    MeView,
    PublisherListView,
    PublisherRegisterView,
    UserDetailView,
    UserListView,
    UserRegisterView,
)

urlpatterns = [
    path("users/register/", UserRegisterView.as_view(), name="user-register"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:user_id>/addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("publishers/register/", PublisherRegisterView.as_view(), name="publisher-register"),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
    path("authors/", AuthorListCreateView.as_view(), name="author-list-create"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),
    path("me/", MeView.as_view(), name="me"),
]
