from django.contrib import admin
from .models import StockBotUser, DeviceToken

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'botID')

class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'platform', 'created_at', 'updated_at')

admin.site.register(StockBotUser, UserAdmin)
admin.site.register(DeviceToken, DeviceTokenAdmin)