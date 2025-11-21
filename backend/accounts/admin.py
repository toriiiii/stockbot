from django.contrib import admin
from .models import StockBotUser

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'botID')

admin.site.register(StockBotUser, UserAdmin)