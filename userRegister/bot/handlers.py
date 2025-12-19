from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from .services.start import handle_start_private_chat
from .services.me import get_user_profile, format_profile_message
from .services.whereami import get_chat_info, format_chat_message

router = Router()

@router.message(Command('start'))
async def start_handler(message: Message):
    '''
    Save users and chats
    '''
    from_user = message.from_user
    chat_data = message.chat
    # If chat is private
    await handle_start_private_chat(from_user=from_user, chat_data=chat_data)
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
        await message.answer('Profile not found. Write /start')
        return
    
    user, membership = result
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
        await message.answer('Chat not registered. Write /start')
        return
    
    chat, memberships = result
    text = format_chat_message(chat=chat, memberships=memberships)
    await message.answer(text, parse_mode=None)

