from django.db.models import Count
from bot.models import TelegramUser, Chat

async def get_stats_private_chat():
    total_users= await TelegramUser.objects.acount()
    total_chats = await Chat.objects.acount()
    user_with_stats = TelegramUser.objects.annotate(
        my_chats_count = Count('membership', distinct=True)
    )
    chat_with_stats = Chat.objects.annotate(
        my_users_count = Count('membership', distinct=True)
    )

    return {
        'total_users': total_users,
        'total_chats': total_chats,
        'user_with_stats': user_with_stats,
        'chat_with_stats': chat_with_stats
    }

    # return total_users, total_chats, user_with_stats, chat_with_stats

def format_stats_message(total_users, total_chats, user_with_stats, chat_with_stats):
    output = [
        'Total statistic:'
        f'Total users: {total_users}'
        f'Total chats: {total_chats}\n'
    ]
    for user in user_with_stats:
        output.append(f'{user.telegram_user_id} stay in  {user.my_chats_count} chats')
    output.append('\n')
    for chat in chat_with_stats:
        output.append(f'{chat.chat_id} have a  {chat.my_users_count} users')

    return '\n'.join(output)

    