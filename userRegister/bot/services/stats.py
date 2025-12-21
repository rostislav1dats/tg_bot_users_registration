import math
from django.db.models import Count, Q
from bot.models import TelegramUser, Chat
from aiogram import types

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class StatsPagination(CallbackData, prefix='stats_page'):
    page: int
    data_type: str

def get_stats_keyboard(page:int, total_pages:int, data_type:str):
    # This function will create and render buttons "back" "forward" "current_page"
    builder = InlineKeyboardBuilder()

    buttons = []
    if page > 1:
        buttons.append(types.InlineKeyboardButton(
            text='<<',
            callback_data=StatsPagination(page=page-1, data_type=data_type).pack())
            )
    buttons.append(types.InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data='ignore'))
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton(
            text='>>',
            callback_data=StatsPagination(page=page+1, data_type=data_type).pack())
            )
    builder.row(*buttons)
    builder.row(
        types.InlineKeyboardButton(text='Users', callback_data=StatsPagination(page=1, data_type='users').pack()),
        types.InlineKeyboardButton(text='Chats', callback_data=StatsPagination(page=1, data_type='chats').pack())
    )
    return builder.as_markup()

async def get_paginated_stats(page: int, data_type: str, limit: int = 2):
    '''
    Logic of get data
    '''
    offset = (page-1) * limit

    if data_type == 'users':
        queryset = TelegramUser.objects.filter().annotate(
            count_val = Count('membership', filter=Q(membership__is_active=True, membership__chat__is_active=True), distinct=True)
        )
        label = 'User'
    else:
        queryset = Chat.objects.filter(is_active=True).annotate(
            count_val = Count('membership', filter=Q(membership__is_active=True), distinct=True)
        )
        label = 'Chat'

    total_count = await queryset.acount()
    total_pages = int(math.ceil(total_count / limit))

    items = []
    async for item in queryset.order_by('-count_val')[offset: offset + limit]:
        if data_type == 'users':
            name = item.first_name or (f'@{item.user_name}' if item.username else f'ID: {item.telegram_user_id}')
            items.append(f'{label} {name} have : {item.count_val} chats')
        else:
            name = item.title or f"ID: {item.chat_id}"
            items.append(f'{label} {name} have : {item.count_val} users')

    return '\n'.join(items), total_pages
