import pytest
from django.utils import timezone

from bot.services.start import handle_start_chat
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
    title = ''

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_start_is_repeated():
    '''
    Test for repeated /start
    '''
    result = await handle_start_chat(from_user=DummyUser(), chat_data=DummyChat())
    user1, chat1, membership1 = result.get('user'), result.get('chat'), result.get('membership')

    assert user1.telegram_user_id == 33437483
    assert chat1.chat_id == 33437483
    assert membership1.user == user1
    assert membership1.chat == chat1

    # Simulate user is leave
    membership1.is_active = False
    membership1.left_at = timezone.now()
    await membership1.asave()

    # Repeat /start
    result = await handle_start_chat(from_user=DummyUser(), chat_data=DummyChat())
    user2, chat2, membership2 = result.get('user'), result.get('chat'), result.get('membership')
    assert user1.id == user2.id
    assert await TelegramUser.objects.acount() == 1
    assert chat1.id == chat2.id
    assert await Chat.objects.acount() == 1
    assert membership1.id == membership2.id
    assert await Membership.objects.acount() == 1
    assert membership2.is_active is True
    

