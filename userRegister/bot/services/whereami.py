from asgiref.sync import sync_to_async
from bot.models import Chat, Membership

async def get_chat_info(chat_data):
    chat, _ = await sync_to_async(Chat.objects.get_or_create)(
        chat_id=chat_data.id,
        defaults={
            "type": getattr(chat_data, "type", "—"),
            "title": getattr(chat_data, "title", "—")
        }
    )

    membership = await sync_to_async(list)(
        Membership.objects.select_related('user').filter(chat=chat, is_active=True)
    )

    return chat, membership
    
def format_chat_message(chat, memberships):
    output = [
        'Current Chat Info\n',
        f'ID: {chat.id};',
        f'Type: {chat.type};',
        f'Title: {chat.title};\n',
        'Active users:\n',
    ]
    if not memberships:
        output.append('---No active chats---')
    else:
        for m in memberships:
            user = f"{m.user.first_name or '-'} || @{m.user.username or '-'} || (ID: {m.user.telegram_user_id})"
            output.append(user)
    return '\n'.join(output)