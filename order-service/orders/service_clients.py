import requests
from django.conf import settings


def request_json(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=5, **kwargs)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def get_book(book_id):
    payload, error = request_json("GET", f"{settings.CATALOG_SERVICE_URL}/api/books/{book_id}/service-detail/")
    return payload, error


def reserve_book(book_id, quantity):
    payload, error = request_json(
        "POST",
        f"{settings.CATALOG_SERVICE_URL}/api/books/{book_id}/reserve/",
        json={"quantity": quantity},
    )
    return payload, error


def get_user(user_id):
    payload, error = request_json("GET", f"{settings.IDENTITY_SERVICE_URL}/api/users/{user_id}/")
    if payload:
        return payload, None
    payload, error = request_json("GET", f"{settings.IDENTITY_SERVICE_URL}/api/publishers/")
    if payload:
        for item in payload:
            if item.get("id") == user_id:
                return item, None
    return None, error or "User not found"
