from django.contrib import admin
from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'initial_grams', 'current_grams', 'expires_at', 'created_at')

admin.site.register(Item, ItemAdmin)