def format_seen(user, chats_queryset):
    output = [
        f'User: {user.username}\n',
        'Asocciated with:',
    ]
    for chat in chats_queryset:
        output.append(f'{chat.title}' if chat.title else f'{chat.id}')
    return '\n'.join(output)