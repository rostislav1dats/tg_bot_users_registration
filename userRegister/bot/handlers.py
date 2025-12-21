from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, KICKED, LEFT

from asgiref.sync import sync_to_async

from .services.start import handle_start_chat
from .services.me import get_user_profile, format_profile_message
from .services.whereami import get_chat_info, format_chat_message
from .services.stats import get_paginated_stats, get_stats_keyboard, StatsPagination
from .services.seen import format_seen
from .models import Membership, TelegramUser, Chat


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
    total_u = await TelegramUser.objects.acount()
    total_c = await Chat.objects.filter(is_active=True).acount()

    items_text, total_pages = await get_paginated_stats(1, 'users')

    text = (
        'General statistic: \n'
        f'Total users: {total_u}\n'
        f'Total chats: {total_c}\n'
        f'\nusers list:\n\n {items_text}'
    )

    await message.answer(text, reply_markup=get_stats_keyboard(1, total_pages, 'users'), parse_mode=None)

@router.callback_query(StatsPagination.filter())
async def process_stats_pagination(callback: types.CallbackQuery, callback_data:StatsPagination):
    items_text, total_pages = await get_paginated_stats(callback_data.page, callback_data.data_type)

    total_u = await TelegramUser.objects.acount()
    total_c = await Chat.objects.filter(is_active=True).acount()

    # Edit text message
    text = (
        'General statistic: \n'
        f'Total users: {total_u}\n'
        f'Total chats: {total_c}\n'
        f'\n{callback_data.data_type} list:\n\n {items_text}'
    )

    await callback.message.edit_text(text, reply_markup=get_stats_keyboard(callback_data.page, total_pages, callback_data.data_type), parse_mode=None)
    await callback.answer()

@router.message(Command('seen'))
async def seen_handler(message: Message, command: CommandObject):
    if message.chat.type == 'private':
        await message.answer('I can handle this command only in group chats')
        return
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
    chats_queryset = Chat.objects.filter(
        membership__user=user,
        is_active=True,
        membership__is_active=True
        )
    text = await sync_to_async(format_seen)(user=user, chats_queryset=chats_queryset)
    await message.answer(text=text, parse_mode=None)

@router.message(Command('forgetme'))
async def forgetme_handler(message: Message):
    user = await TelegramUser.objects.filter(telegram_user_id=message.from_user.id).afirst()
    
    if not user:
        await message.answer('U didnt registered in any chat')
        return
    await Membership.objects.filter(user=user).aupdate(is_active=False)
    await message.answer('Success deleted you from our bot')

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT), F.chat.type == 'private')
async def user_blocked_bot(event: types.ChatMemberUpdated):
    '''
    User delete or block Bot
    '''
    user_id = event.from_user.id
    # Update data in DB
    await Membership.objects.filter(user__telegram_user_id=user_id).aupdate(is_active=False)
    print(f'User {user_id} blocked bot')

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT), F.chat.type.in_({'group', 'supergroup'}))
async def bot_removed_from_chat(event: types.ChatMemberUpdated):
    '''
    Set inactive chats where bot was kicked
    '''
    chat_id = event.chat.id
    # mark chat as inactive
    await Chat.objects.filter(chat_id=chat_id).aupdate(is_active=False)
    # mark all associations with this chat as inactive
    await Membership.objects.filter(chat__chat_id=chat_id).aupdate(is_active=False)
    print(f'Bot was deleted from chat {chat_id} chat is deactivated')

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT))
async def user_left_chat(event: types.ChatMemberUpdated):
    '''
    If user left chat or have been kicked
    '''
    chat_id = event.chat.id
    user_id = event.from_user.id
    
    await Membership.objects.filter(
        chat__chat_id=chat_id,
        user__telegram_user_id=user_id
    ).aupdate(is_active=False)
    print(f'User {user_id} left chat {chat_id}')

@router.message(F.chat.type == 'private')
async def echo_all(message: Message):
    await message.answer(
        'I don`t quite understang your message.\n'
        'Please, input /help to see what I can do'
    )
