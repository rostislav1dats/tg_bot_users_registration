from django.db import models

class TelegramUser(models.Model):
    telegram_user_id = models.CharField(max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username}' if self.username  else f'{self.telegram_user_id}'
    
class Chat(models.Model):
    CHAT_TYPES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('supergroup', 'Supergroup'),
        ('channel', 'Channel'),
    ]

    chat_id = models.CharField(max_length=255, unique=True, db_index=True)
    type = models.CharField(max_length=20, choices=CHAT_TYPES)
    is_active = models.BooleanField(default=True)
    bot_left_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.type in ('group', 'supergroup', 'channel'):
            return f'{self.title or self.chat_id} ({self.type})'
        return f'Private chat ({self.chat_id})'
    
class Membership(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'chat')
