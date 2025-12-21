from aiogram import Bot
from django.conf import settings

async def set_webhook(webhook, secret_token, allowed_updates):
    bot = Bot(token=settings.BOT_TOKEN)
    await bot.set_webhook(
        url=f'{webhook}/telegram/webhook/',
        secret_token=secret_token,
        allowed_updates=allowed_updates
    )
    print('success')
