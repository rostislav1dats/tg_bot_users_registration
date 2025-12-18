from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import TelegramUser, Chat, Membership
from .services import normalize

router = Router()

@router.message(F.text == '/start')
async def start_handler(message: Message):
    # Check this is private chat
    print(f'{message.from_user}')
    if message.chat.type != 'private':
        await message.answer('Please write to my private chat.')
        return
    
    from_user = message.from_user
    chat_data = message.chat

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
            'type': 'private',
            'title': None,
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

    await message.answer(
        f'Hi, {from_user.first_name or from_user.username or ''} \n'
        'I saved info about you.'
    )

# @router.message()
# async def echo(message: types.Message):
#     await message.answer(f'Your wrote: {message.text}')
