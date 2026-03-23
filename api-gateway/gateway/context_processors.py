def gateway_context(request):
    return {
        "current_user": request.session.get("user"),
        "cart_count": request.session.get("cart_count", 0),
    }
