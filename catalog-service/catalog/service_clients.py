from decimal import Decimal

import requests
from django.conf import settings


def fetch_json(url):
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_user_display(user_id):
    payload = fetch_json(f"{settings.IDENTITY_SERVICE_URL}/api/users/{user_id}/")
    if payload:
        return f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
    payload = fetch_json(f"{settings.IDENTITY_SERVICE_URL}/api/publishers/")
    if payload:
        for item in payload:
            if item.get("id") == user_id:
                return f"{item.get('first_name', '')} {item.get('last_name', '')}".strip()
    return ""


def get_author_display(author_id):
    payload = fetch_json(f"{settings.IDENTITY_SERVICE_URL}/api/authors/{author_id}/")
    if not payload:
        return ""
    return f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()


def normalize_decimal(value):
    return Decimal(str(value))
