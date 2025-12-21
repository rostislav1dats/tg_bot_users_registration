from django.db.models import Prefetch
from bot.models import Chat, Membership

async def get_chat_info(chat_data):
    # Get chat and all users active in this chat
    chat = await Chat.objects.prefetch_related(
        Prefetch(
            'membership', # Related name in model Membership for association with users
            queryset=Membership.objects.filter(is_active=True).select_related('user'),
            to_attr = 'active_memberships'
        )
    ).filter(chat_id=chat_data.id).afirst()

    if not chat:
        return None

    return {
        'chat': chat,
        'membership': chat.active_memberships,
    }
 
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
