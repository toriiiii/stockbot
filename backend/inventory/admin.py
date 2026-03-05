from django.contrib import admin
from .models import Item, SensorIngestionEvent

class ItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'initial_grams', 'current_grams', 'expires_at', 'created_at')

class SensorIngestionEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_id', 'classification', 'weight_grams', 'expires_at', 'created_at')

admin.site.register(Item, ItemAdmin)
admin.site.register(SensorIngestionEvent, SensorIngestionEventAdmin)