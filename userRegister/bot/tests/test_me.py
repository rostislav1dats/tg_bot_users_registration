from unittest.mock import AsyncMock, patch
import pytest
from bot.models import TelegramUser, Chat, Membership
from bot.handlers import me_handler
from asgiref.sync import sync_to_async

@patch('aiogram.types.message.Message.answer', new_callable=AsyncMock)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_with_chats(bot, message_factory):
    '''
    User exists and have chats
    What we check:
    - user is found
    - returns memberships
    - in text we have ID, username, groups list
    '''
    user = await sync_to_async(TelegramUser.objects.create)(
        telegram_user_id=1,
        username='testuser'
    )
    message = message_factory(from_user_id=1, text='/me')
    chat = await sync_to_async(Chat.objects.create)(
        chat_id=100,
        type='group',
        title='Test Group'
    )
    await sync_to_async(Membership.objects.create)(user=user, chat=chat, is_active=True)

    await me_handler(message)
    message.answer.assert_called()
    text = message.answer.call_args.args[0]

    assert 'testuser' in text
    assert 'Test Group' in text

@patch('aiogram.types.message.Message.answer', new_callable=AsyncMock)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_without_chats(bot, message_factory):
    '''
    User exists but don`t have chats
    '''
    await sync_to_async(TelegramUser.objects.create)(
        telegram_user_id=923248394839,
    )
    message = message_factory(from_user_id=923248394839, text='/me')
    await me_handler(message)
    text = message.answer.call_args.args[0]
    assert '---No active chats---' in text

@patch('aiogram.types.message.Message.answer', new_callable=AsyncMock)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_user_not_found(bot, message_factory):
    '''
    User don`t found 
    '''
    message = message_factory(text='/me', from_user_id=999)
    await me_handler(message)
    message.answer.assert_called_with('Profile not found. Write /start')

@patch('aiogram.types.message.Message.answer', new_callable=AsyncMock)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_empty_fields(bot, message_factory):
    '''
    If fields are empty (username and name)
    '''
    await sync_to_async(TelegramUser.objects.create)(
        telegram_user_id=10,
        username=None,
        first_name=None,
        last_name=None
    )
    message = message_factory(text='/me', from_user_id=10)
    await me_handler(message)
    text = message.answer.call_args.args[0]
    assert 'Username: ---' in text
    assert 'Name: - ' in text

@patch('aiogram.types.message.Message.answer', new_callable=AsyncMock)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_many_chats(bot, message_factory):
    '''
    check performance
    a lot of chats
    '''
    user = await sync_to_async(TelegramUser.objects.create)(telegram_user_id=666)
    for i in range(500, 600):
        chat = await sync_to_async(Chat.objects.create)(chat_id=i, type='group')
        await sync_to_async(Membership.objects.create)(user=user, chat=chat, is_active=True)

    message = message_factory(text='/me', from_user_id=666)

    await me_handler(message)

    text = message.answer.call_args.args[0]
    assert text.count('') == 2276
