from django.utils import timezone
from asgiref.sync import sync_to_async
from bot.models import TelegramUser, Chat, Membership
from .normilize import normalize

async def handle_start_private_chat(from_user, chat_data):
    # Create or update user
    user, _ = await sync_to_async(TelegramUser.objects.update_or_create)(
        telegram_user_id = from_user.id,
        defaults = {
            'username': normalize(from_user.username),
            'first_name': normalize(from_user.first_name),
            'last_name': normalize(from_user.last_name),
            'language_code': normalize(from_user.language_code),
            'is_bot': from_user.is_bot,
        }
    )

    # Create or update private chat
    chat, _ = await sync_to_async(Chat.objects.update_or_create)(
        chat_id = chat_data.id,
        defaults = {
            'type': chat_data.type,
            'title': chat_data.title,
            'is_active': True,
            'bot_left_at': None,
        }
    )

    # User <-> Chat connection (Membership)
    membership, created = await sync_to_async(Membership.objects.get_or_create)(
        user = user,
        chat = chat,
        defaults = {
            'is_active': True,
            'joined_at': timezone.now(),
        }
    )

    # If user came back after deleting chat
    if not created and not membership.is_active:
        membership.is_active = True
        membership.left_at = None
        await sync_to_async(membership.save)()

    return user, chat, membership
