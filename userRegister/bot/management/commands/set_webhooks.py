import asyncio
from django.conf import settings
from django.core.management.base import BaseCommand
from bot.services import set_webhook

class Command(BaseCommand):
    help = 'Set telegram webhook'

    def handle(self, *args, **kwargs):
        webhook, secret_token = settings.WEBHOOK_URL, settings.WEBHOOK_SECRET
        if not webhook:
            self.stdout.write(self.style.ERROR('No active webhook found'))
            return
        asyncio.run(set_webhook(webhook, secret_token))
        self.stdout.write(self.style.SUCCESS('Webhook succesfully set'))
