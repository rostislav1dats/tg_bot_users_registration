import pytest
from django.utils import timezone
from asgiref.sync import sync_to_async

from bot.services.start import handle_start_private_chat
from bot.models import TelegramUser, Chat, Membership

class DummyUser:
    id = 33437483
    username = 'testuser'
    first_name = 'Test'
    last_name = None
    language_code = 'en'
    is_bot = False

class DummyChat:
    id = 33437483
    type = 'private'

# Test for repeated /start
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_start_is_repeated():
    user1, chat1, membership1 = await handle_start_private_chat(from_user=DummyUser(), chat_data=DummyChat())

    assert user1.telegram_user_id == 33437483
    assert chat1.chat_id == 33437483
    assert membership1.user == user1
    assert membership1.chat == chat1

    # Simulate user is leave
    membership1.is_active = False
    membership1.left_at = timezone.now()
    await sync_to_async(membership1.save)()

    # Repeat /start
    user2, chat2, membership2 = await handle_start_private_chat(from_user=DummyUser(), chat_data=DummyChat())
    assert user1.id == user2.id
    assert await sync_to_async(TelegramUser.objects.count)() == 1
    assert chat1.id == chat2.id
    assert await sync_to_async(Chat.objects.count)() == 1
    assert membership1.id == membership2.id
    assert await sync_to_async(Membership.objects.count)() == 1
    assert membership2.is_active is True
    assert membership2.left_at is None

