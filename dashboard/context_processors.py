def tenant_branding(request):
    return {"tenant": getattr(request, "tenant", None)}
