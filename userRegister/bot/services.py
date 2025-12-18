from aiogram import Bot
from django.conf import settings

async def set_webhook(webhook, secret_token):
    bot = Bot(token=settings.BOT_TOKEN)
    await bot.set_webhook(
        url=f'{webhook}/telegram/webhook/',
        secret_token=secret_token
    )
    print('success')

def normalize(value: str | None) -> str | None:
    if value:
        value = value.strip()
        return value if value else None
    return None
