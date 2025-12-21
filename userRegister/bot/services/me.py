from bot.models import TelegramUser, Membership

async def get_user_profile(telegram_user_id: id):
    try:
        user = await TelegramUser.objects.aget(telegram_user_id=telegram_user_id)
    except TelegramUser.DoesNotExist:
        return None

    membership_qs = Membership.objects.select_related('chat').filter(
        user=user,
        is_active = True
    )

    membership = [m async for m in membership_qs]

    return {
        'user': user,
        'membership': membership,
    }

def format_profile_message(user, memberships):
    output = [
        'Your profile:\n',
        f'ID: {user.telegram_user_id};',
        f'Username: @{user.username or '-'};' if user.username else 'Username: ---;',
        f'Name: {user.first_name or '-'} {user.last_name or ''};'.strip(),
        f'Language: {user.language_code or '-'}. \n',
        'Chats:\n'
    ]

    if not memberships:
        output.append('---No active chats---')
    else: 
        for m in memberships:
            title = m.chat.title or 'Private chat'
            output.append(f'{m.chat.type} || {title}')
    return '\n'.join(output)
