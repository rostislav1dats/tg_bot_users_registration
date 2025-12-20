from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from asgiref.sync import sync_to_async

from .services.start import handle_start_chat
from .services.me import get_user_profile, format_profile_message
from .services.whereami import get_chat_info, format_chat_message
from .services.stats import get_stats_private_chat, format_stats_message
from .services.seen import format_seen
from .models import TelegramUser, Chat


router = Router()

@router.message(Command('start'))
async def start_handler(message: Message):
    '''
    Save users and chats
    '''
    from_user = message.from_user
    chat_data = message.chat
    # If chat is private
    await handle_start_chat(from_user=from_user, chat_data=chat_data)
    await message.answer(
        f'Hi, {from_user.first_name or from_user.username or ''}, \n'
        'I saved info about you.'
    )

@router.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(
        'Here is all list of my commands: \n'
        '/start — greet; confirm persistence for the current user & chat \n'
        '/help — show available commands \n'
        '/me — show stored profile details for the current user \n'
        '/whereami — show stored details for the current chat \n'
        '/stats — show counts: total users, total chats, users per chat, chats per user (for the invoker) (Private only) \n'
        '/seen @username — show whether that user is known and in which chats they’ve been seen (Groups only) \n'
    )

@router.message(Command('me'))
async def me_handler(message: Message):
    '''
    Get info about user and subscribed chats
    '''
    result = await get_user_profile(message.from_user.id)

    if result is None:
        result = await handle_start_chat(from_user=message.from_user, chat_data=message.chat.data)
    
    user, membership, = result.get('user'), result.get('membership')
    text = format_profile_message(user, membership)
    await message.answer(text, parse_mode=None)

@router.message(Command('whereami'))
async def whereami_handler(message: Message):
    '''
    Get info about Chat and included users
    '''
    chat_data = message.chat
    result = await get_chat_info(chat_data=chat_data)

    if result is None:
        result = await handle_start_chat(from_user=message.from_user, chat_data=message.chat.data)
    
    chat, memberships = result.get('chat'), result.get('membership')
    text = format_chat_message(chat=chat, memberships=memberships)
    await message.answer(text, parse_mode=None)

@router.message(Command('stats'))
async def stats_handler(message: Message):
    chat_data = message.chat
    if chat_data.type == 'private':
        result = await get_stats_private_chat()
        text = await sync_to_async(format_stats_message)(
            result.get('total_users'),
            result.get('total_chats'),
            result.get('user_with_stats'),
            result.get('chat_with_stats')
            )
        await message.answer(text=text, parse_mode=None)
    else:
        await message.answer('I can handle this command only in private chat')

@router.message(Command('seen'))
async def seen_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer('ERROR! input: `/seen @username` or `/seen 12345`')
        return
    
    clean_input = command.args.strip().replace("@", "").strip()

    # Search User || check is input username or user_id
    try:
        if clean_input.isdigit():
            user = await TelegramUser.objects.aget(id=int(clean_input))
        else:
            user = await TelegramUser.objects.aget(username__iexact=clean_input)
    except TelegramUser.DoesNotExist:
        await message.reply('Wrong format: use @username or nummeric user_id')
        return None, None
    
    # Get all chats asocciated with user
    chats_queryset = Chat.objects.filter(membership__user=user)
    text = await sync_to_async(format_seen)(user=user, chats_queryset=chats_queryset)
    await message.answer(text=text, parse_mode=None)
