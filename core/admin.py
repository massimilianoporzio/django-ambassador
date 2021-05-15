from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User


# Register your models here.
@admin.register(User)
class SuperUser(admin.ModelAdmin):
    ordering = ['id']
    model=User

