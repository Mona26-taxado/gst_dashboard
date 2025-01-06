from django.shortcuts import redirect
from django.http import HttpResponseForbidden




def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator






#To ensure extra security across all views, you can add middleware that checks the role before allowing access to the update_pin view.
class AdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is accessing the update-pin view
        if 'update-pin' in request.path and request.user.role != 'admin':
            return HttpResponseForbidden("You do not have permission to access this page.")
        return self.get_response(request)
