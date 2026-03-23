import requests
from django.conf import settings


def call_service(method, url, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method, url, headers=headers, timeout=8, **kwargs)
        data = None
        if response.content:
            try:
                data = response.json()
            except ValueError:
                data = {"raw": response.text}
        if response.status_code >= 400:
            return data or {"detail": response.text}, response.status_code
        return data, response.status_code
    except requests.RequestException as exc:
        return {"detail": str(exc)}, 502


def identity_url(path):
    return f"{settings.IDENTITY_SERVICE_URL}{path}"


def catalog_url(path):
    return f"{settings.CATALOG_SERVICE_URL}{path}"


def order_url(path):
    return f"{settings.ORDER_SERVICE_URL}{path}"
