import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from aiogram.types import Update

from .aigram_app import bot, dp

@csrf_exempt
async def telegram_webhook(request):
    '''
        get http request from telegram
        check that webhook is On and real
        convert input data in Update object
        send data to aiogram app for handlers processing 
        return {"ok": True}
    '''
    secret = (
        request.headers.get("X-Telegram-Bot-Api-Secret-Token") or
        request.META.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN")
    )

    if request.method != "POST":
        return JsonResponse({"ok": True})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    if secret != settings.WEBHOOK_SECRET:
        return HttpResponseForbidden('Secret is invalid')
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    
    update = Update.model_validate(data)

    await dp.feed_update(bot, update)
    return JsonResponse({"ok": True})
