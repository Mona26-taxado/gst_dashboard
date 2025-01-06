from dashboard.models import CustomUser

def get_custom_user_by_username(username):
    return CustomUser.objects.get(username=username)
