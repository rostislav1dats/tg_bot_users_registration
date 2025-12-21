# Django user register bot  
my telegram bot for save user, chats and users in chat  

## Project opportunities
- Telegram bot remembers:  
  - users;  
  - chats;  
  - memberships (model for asociatioan Many2Many between users and chats).
- Support messages from private chats and group/supergroup contexts.  
- Handle bot being removed from group; use ChatMemberUpdatedFilter.
- Avoid duplicate records. Using acreate_or_update method.  

## Storage options  
I`m use PostgreSQL because this support async / await  
Many advanced features of Django ORM (such as distinct() on specific fields, specific aggregations, indexes, and full-text search) only work on PostgreSQL.  
Easy scalability. If you need a second server, you can simply connect it to the existing database. SQLite supports only one connection.  

## Webhook  
Telegram sends the message to your server as soon as it appears. The code “sleeps” and is activated only when there is real work to be done.  
Can use secret_token in Webhook (as I already did) so that the server only accepts requests from Telegram.  

## Config 
BOT_TOKEN=<YOUR_BOT_TOKEN>  
SECURITY_KEY=<YOUR_SECURITY_TOKEN>  
WEBHOOK_URL=<YOUR_WEBHOOK_URL>  
WEBHOOK_SECRET=<YOUR_SECRET_KEY>  
PG_ENGINE='django.db.backends.postgresql'  
PG_NAME=<YOUR_DB_NAME>  
PG_USER=<YOUR_DB_USER>  
PG_PASSWORD=<YOUR_DB_PASSWORD>  
PG_HOST=<YOUR_DB_HOST>  
PG_PORT=<YOUR_DB_PORT>  

## Deployment  
(first time)
1) python manage.py collectstatic
2) python manage.py makemigrations
3) python manage.py migrate
4) python manage.py createsuperuser  
5) python manage.py set_webhooks  
6) uvicorn userRegister.asgi:application --reload  
(second time and next)
1) python manage.py set_webhooks
2) uvicorn userRegister.asgi:application --reload

## Up bot in one command
>> cd userRegister

>> docker-compose up --build

## Unit tests
1) pytest bot/tests/test_start.py (repeats user saving without repeating database entries, but only updating fields)  
2) pytests bot/tests/test_me.py (checking the operation of the /me command if the user has no chats; if the user has empty first_name and username fields; testing the bot's load)  

## Architecture
<img width="404" height="759" alt="image" src="https://github.com/user-attachments/assets/24d9e12c-dcc6-4ece-8f11-288b0514b207" />  

## /start 

<img width="317" height="132" alt="image" src="https://github.com/user-attachments/assets/363814ab-ae43-4c6c-9614-27db0343313f" />  

## /whereami  

<img width="490" height="332" alt="image" src="https://github.com/user-attachments/assets/297d6867-97b0-412f-90fb-10720f6567c4" />  

## /stats  

<img width="350" height="398" alt="image" src="https://github.com/user-attachments/assets/65181179-6298-4961-bdbd-9e1f3bb98ef7" />  

## /seen @username  

<img width="588" height="350" alt="image" src="https://github.com/user-attachments/assets/70ea3a6f-dbc3-4420-8237-1e53ed6a3cf3" />  

## what can be done for scalability:
- add a load balancer;
- add localization while keeping all messages in the database;
- add inlinekeyboard for the remaining commands (/me, /whereami, /seen);
- add administrator role for more detailed statistics.  





