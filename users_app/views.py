import json

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot

from users_app.forms import ServiceForm, ServiceKeyForm
from users_app.models import NumbersService, Rules, Key, User


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('about')
        else:
            error_message = "Неверный логин или пароль."

    return render(request, 'html/login.html', {'error_message': error_message})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def about_view(request):
    return render(request, 'html/about.html')


@login_required
def index(request):
    return render(request, 'html/index.html')


@login_required
def faq(request):
    return render(request, 'html/a_faq.html')


@login_required
def settings_rules(request):
    if request.method == 'POST':
        form = ServiceForm(user=request.user, data=request.POST)
        if form.is_valid():
            sender = form.cleaned_data['sender']
            telephone = form.cleaned_data['telephone']
            telegram_chat = form.cleaned_data['telegram_chat']

            Rules.objects.create(
                user=request.user,
                sender=sender,
                from_whom=telephone,
                to_whom=telegram_chat
            )

            return redirect('settings_rules')

    else:
        form = ServiceForm(user=request.user)

    # Получаем все правила для текущего пользователя
    user_rules = Rules.objects.filter(user=request.user)

    return render(request, 'html/a_my_forms.html', {'form': form, 'user_rules': user_rules})


@login_required
def delete_rule(request, rule_id):
    # Получаем объект по его ID
    rule = get_object_or_404(Rules, id=rule_id, user=request.user)

    # Удаляем объект
    if request.method == 'POST':
        rule.delete()
        return redirect('settings_rules')  # Перенаправляем обратно на страницу настроек

    # Если метод не POST, то просто показываем страницу с подтверждением
    return render(request, 'html/confirm_delete.html', {'rule': rule})


@login_required
def settings_service(request):
    if request.method == 'POST':
        form = ServiceKeyForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            name = form.cleaned_data['name']

            if service == 'Novofon':
                telephone = form.cleaned_data['telephone']
                NumbersService.objects.create(user=request.user, name=service, telephone=telephone)
                return JsonResponse({"success": True})
            else:
                key = form.cleaned_data['key']
                Key.objects.create(user=request.user, name=service, title=name, token=key)
                return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = ServiceKeyForm()

    user_keys = Key.objects.filter(user=request.user)

    return render(request, 'html/a_my_input.html', {'form': form, 'user_keys': user_keys})


@login_required
def delete_service(request, key_id):
    key = get_object_or_404(Key, id=key_id, user=request.user)

    if request.method == 'POST':
        key.delete()
        return redirect('settings_service')

    return render(request, 'html/confirm_delete.html', {'key': key})


@csrf_exempt
async def get_webhook(request, token):
    if request.method == 'POST':
        try:
            try:
                user = await sync_to_async(User.objects.get)(token_url=token)
            except User.DoesNotExist:
                return HttpResponseForbidden('Неверный токен')

            data = json.loads(request.body)

            if 'result' in data:
                result = data['result']
                caller_did = result.get('caller_did', 'Не указан')
                caller_id = result.get('caller_id', 'Не указан')
                text = result.get('text', 'Не указан')

                rules = await sync_to_async(Rules.objects.filter)(user=user)
                matched_rule = await sync_to_async(rules.filter(sender=caller_id).first)()

                if matched_rule:
                    to_whom_chat_id = await sync_to_async(lambda: matched_rule.to_whom.chat_id)()

                    tg_bot = Bot(settings.TOKEN_BOT)
                    message_text = (f'Пришло сообщение от {caller_id}\n'
                                    f'На номер: {caller_did}\n'
                                    f'Текст: {text}')
                    await tg_bot.send_message(chat_id=to_whom_chat_id, text=message_text)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Данные получены',
                        'rule_id': matched_rule.id
                    }, status=200)
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Данные получены, но правило не найдено'
                    }, status=200)

            else:
                return JsonResponse({'status': 'error', 'message': 'Ключ "result" отсутствует'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Только POST-запросы поддерживаются'}, status=405)
