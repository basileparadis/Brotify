from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User

from accounts.models import UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class Utilisateur(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'utilisateurs'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (Utilisateur,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
