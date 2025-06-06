from django.contrib import admin
from .models import CustomUser
from .models import Equipment

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')




admin.site.register(Equipment)


