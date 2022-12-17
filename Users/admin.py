from django.contrib import admin
from .models import MyUser, UserProfile
# Register your models here.

class MyUserAdmin(admin.ModelAdmin):
    model=MyUser
    list_display=[
        "email", "Fullname"
    ]
    list_filter=[
        "is_superuser"
    ]
    filter_horizontal=()
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(UserProfile)
