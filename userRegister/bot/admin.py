from django.contrib import admin
from .models import TelegramUser, Chat, Membership

admin.site.register(TelegramUser)
admin.site.register(Chat)
admin.site.register(Membership)
