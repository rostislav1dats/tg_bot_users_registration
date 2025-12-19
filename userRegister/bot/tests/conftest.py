from unittest.mock import AsyncMock
from datetime import datetime
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Chat, User, Message
import pytest

@pytest.fixture
def bot():
    bot = Bot(
        token="123456:TESTTOKEN",
        default=DefaultBotProperties(parse_mode='Markdown')
    )

    bot.session.make_request = AsyncMock()
    return bot

@pytest.fixture
def message_factory(bot):
    def factory(
        *,
        text="/me",
        from_user_id=1,
        username="testuser",
        first_name="Test",
        last_name=None,
        chat_id=100,
        chat_type="private",
        chat_title=None,
    ):
        raw_message = {
            "message_id": 1,
            "date": int(datetime.now().timestamp()),
            "chat": {
                "id": chat_id,
                "type": chat_type,
                "title": chat_title,
            },
            "from": {
                "id": from_user_id,
                "is_bot": False,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "language_code": "en",
            },
            "text": text,
        }

        message = Message.model_validate(raw_message)
        message.__dict__answer = AsyncMock()
        message.__dict__reply = AsyncMock()

        return message

    return factory
