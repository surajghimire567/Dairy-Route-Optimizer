from django.contrib import admin
from .models import Cafe, Visit


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("cafe", "date")