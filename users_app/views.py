import json
import logging
import time
from django.db import connections

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import OperationalError
from telegram import Bot

from users_app.forms import ServiceForm, ServiceKeyForm
from users_app.models import NumbersService, Rules, Key, User

logger = logging.getLogger(__name__)


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"Успешный вход пользователя: {user.phone} (ID: {user.id})")
            return redirect('about')
        else:
            error_message = "Неверный логин или пароль."
            logger.warning(f"Неудачная попытка входа для пользователя: {username}")

    return render(request, 'html/login.html', {'error_message': error_message})


@login_required
def logout_view(request):
    user_info = f"{request.user.phone} (ID: {request.user.id})"
    logout(request)
    logger.info(f"Пользователь вышел из системы: {user_info}")
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
            logger.info(f"Форма создания правила прошла валидацию для пользователя {request.user.phone}")
            # Проверяем, установлен ли флаг "Любой отправитель"
            any_sender = form.cleaned_data.get('any_sender', False)
            if any_sender:  # Если флаг установлен
                sender = 'Любой отправитель'
            else:
                sender = form.cleaned_data['sender']

            telephone = form.cleaned_data['telephone']
            telegram_chat = form.cleaned_data['telegram_chat']

            # Создаем правило с учетом флага
            rule = Rules.objects.create(
                user=request.user,
                sender=sender,
                from_whom=telephone,
                to_whom=telegram_chat
            )
            
            logger.info(f"Создано новое правило (ID: {rule.id}) для пользователя {request.user.phone}: {sender} -> {telegram_chat.title}")

            return redirect('settings_rules')

        else:
            # Выводим ошибки, если форма невалидна
            logger.warning(f"Ошибки в форме создания правила для пользователя {request.user.phone}: {form.errors}")

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
        rule_info = f"Rule ID: {rule.id}, Sender: {rule.sender}, From: {rule.from_whom.telephone}"
        rule.delete()
        logger.info(f"Пользователь {request.user.phone} удалил правило: {rule_info}")
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
                number_service = NumbersService.objects.create(user=request.user, name=service, telephone=telephone)
                logger.info(f"Пользователь {request.user.phone} добавил номер Novofon: {telephone}")
                return JsonResponse({"success": True})
            else:
                key = form.cleaned_data['key']
                api_key = Key.objects.create(user=request.user, name=service, title=name, token=key)
                logger.info(f"Пользователь {request.user.phone} добавил API ключ {service}: {name}")
                return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = ServiceKeyForm()

    # Получаем все объекты для текущего пользователя
    user_keys = Key.objects.filter(user=request.user)
    user_numbers = NumbersService.objects.filter(user=request.user)

    return render(
        request,
        'html/a_my_input.html',
        {'form': form, 'user_keys': user_keys, 'user_numbers': user_numbers}
    )


@login_required
def delete_number_service(request, id):
    service = get_object_or_404(NumbersService, id=id, user=request.user)
    service_info = f"Service: {service.name}, Phone: {service.telephone}"
    service.delete()
    logger.info(f"Пользователь {request.user.phone} удалил номер сервиса: {service_info}")
    return redirect('settings_service')


@login_required
def delete_service(request, key_id):
    key = get_object_or_404(Key, id=key_id, user=request.user)

    if request.method == 'POST':
        key_info = f"Service: {key.name}, Title: {key.title}"
        key.delete()
        logger.info(f"Пользователь {request.user.phone} удалил API ключ: {key_info}")
        return redirect('settings_service')

    return render(request, 'html/confirm_delete.html', {'key': key})


async def get_user_by_token_with_retry(token, max_retries=3):
    """Получение пользователя по токену с ретраями"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 WEBHOOK: попытка {attempt + 1} получения пользователя по токену {token[:8]}...")
            user = await sync_to_async(User.objects.get)(token_url=token)
            logger.info(f"✅ WEBHOOK: пользователь найден: {user.phone} (ID: {user.id})")
            return user
        except User.DoesNotExist:
            logger.warning(f"❌ WEBHOOK: пользователь с токеном {token[:8]}... не найден")
            return None
        except OperationalError as e:
            if e.args[0] in (2006, 2013):  # MySQL connection errors
                logger.warning(f"⚠️ WEBHOOK: ошибка подключения к БД (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    connections.close_all()
                    await sync_to_async(time.sleep)(0.5 * (2 ** attempt))
                    continue
            raise
        except Exception as e:
            logger.error(f"💥 WEBHOOK: неожиданная ошибка при получении пользователя: {e}")
            raise
    
    logger.error(f"💥 WEBHOOK: все попытки получения пользователя исчерпаны")
    raise Exception("Failed to get user after all retries")


async def get_rules_with_retry(user, max_retries=3):
    """Получение правил пользователя с ретраями"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 WEBHOOK: попытка {attempt + 1} получения правил для пользователя {user.phone}")
            # Используем select_related для загрузки связанных объектов
            rules_queryset = Rules.objects.filter(user=user).select_related('to_whom', 'from_whom')
            rules_list = await sync_to_async(lambda: list(rules_queryset))()
            logger.info(f"✅ WEBHOOK: найдено {len(rules_list)} правил для пользователя {user.phone}")
            return rules_list
        except OperationalError as e:
            if e.args[0] in (2006, 2013):  # MySQL connection errors
                logger.warning(f"⚠️ WEBHOOK: ошибка подключения к БД при получении правил (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    connections.close_all()
                    await sync_to_async(time.sleep)(0.5 * (2 ** attempt))
                    continue
            raise
        except Exception as e:
            logger.error(f"💥 WEBHOOK: ошибка при получении правил: {e}")
            raise
    
    logger.error(f"💥 WEBHOOK: все попытки получения правил исчерпаны")
    raise Exception("Failed to get rules after all retries")


@csrf_exempt
async def get_webhook(request, token):
    # Логируем КАЖДЫЙ запрос с временной меткой
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
    
    logger.info(f"🌍 WEBHOOK ЗАПРОС [{timestamp}]: {request.method} от IP {client_ip}, токен: {token[:8]}...")
    
    if request.method != 'POST':
        logger.warning(f"❌ WEBHOOK: неподдерживаемый метод {request.method}")
        return JsonResponse({'status': 'error', 'message': 'Только POST-запросы поддерживаются'}, status=405)

    try:
        # Логируем сырые данные запроса
        raw_body = request.body
        logger.info(f"📥 WEBHOOK: получены сырые данные ({len(raw_body)} байт): {raw_body[:500]}")
        
        # Парсим JSON
        try:
            data = json.loads(raw_body)
            logger.info(f"📋 WEBHOOK: JSON успешно распарсен: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"💥 WEBHOOK: ошибка парсинга JSON: {e}")
            logger.error(f"💥 WEBHOOK: проблемные данные: {raw_body}")
            return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON'}, status=400)

        # Получаем пользователя
        user = await get_user_by_token_with_retry(token)
        if user is None:
            return HttpResponseForbidden('Неверный токен')

        # Ищем данные SMS в разных форматах Novofon
        sms_data = None
        
        # Вариант 1: данные в корне
        if all(key in data for key in ['caller_id', 'caller_did', 'text']):
            sms_data = data
            logger.info(f"📱 WEBHOOK: обнаружен формат SMS в корне JSON")
            
        # Вариант 2: данные в блоке 'result'
        elif 'result' in data and isinstance(data['result'], dict):
            result = data['result']
            if all(key in result for key in ['caller_id', 'caller_did', 'text']):
                sms_data = result
                logger.info(f"📱 WEBHOOK: обнаружен формат SMS в блоке 'result'")
                
        # Вариант 3: другие возможные вложенности
        elif 'data' in data and isinstance(data['data'], dict):
            if all(key in data['data'] for key in ['caller_id', 'caller_did', 'text']):
                sms_data = data['data']
                logger.info(f"📱 WEBHOOK: обнаружен формат SMS в блоке 'data'")

        if sms_data is None:
            logger.warning(f"❌ WEBHOOK: не найдены данные SMS в известных форматах")
            logger.warning(f"❌ WEBHOOK: структура данных: {list(data.keys())}")
            return JsonResponse({'status': 'error', 'message': 'Данные SMS не найдены в известных форматах'}, status=400)

        # Извлекаем данные SMS
        caller_id = sms_data.get('caller_id', 'Не указан')
        caller_did = sms_data.get('caller_did', 'Не указан') 
        text = sms_data.get('text', 'Не указан')

        logger.info(f"📱 WEBHOOK: SMS данные извлечены:")
        logger.info(f"   📞 От: {caller_id}")
        logger.info(f"   📞 На: {caller_did}")
        logger.info(f"   💬 Текст: {text[:100]}{'...' if len(text) > 100 else ''}")

        # Получаем правила с ретраями
        rules = await get_rules_with_retry(user)
        
        # Фильтруем подходящие правила
        matched_rules = []
        for rule in rules:
            from_whom_phone = rule.from_whom.telephone if rule.from_whom else 'Не указан'
            logger.info(f"🔍 WEBHOOK: проверка правила ID {rule.id}: '{rule.sender}' (номер: {from_whom_phone}) -> {rule.to_whom.title if rule.to_whom else 'None'}")
            
            # Проверяем отправителя И получателя SMS
            sender_matches = rule.sender in [caller_id, "Любой отправитель"]
            recipient_matches = rule.from_whom and rule.from_whom.telephone == caller_did
            
            if sender_matches and recipient_matches:
                matched_rules.append(rule)
                logger.info(f"✅ WEBHOOK: правило ID {rule.id} подходит (отправитель: {sender_matches}, получатель: {recipient_matches})")
            else:
                logger.info(f"❌ WEBHOOK: правило ID {rule.id} не подходит (отправитель: {sender_matches}, получатель: {recipient_matches})")

        logger.info(f"📋 WEBHOOK: найдено {len(matched_rules)} подходящих правил из {len(rules)} общих")

        if matched_rules:
            logger.info(f"🚀 WEBHOOK: начинаем отправку в Telegram...")
            tg_bot = Bot(settings.TOKEN_BOT)
            sent_count = 0
            
            for rule in matched_rules:
                try:
                    logger.info(f"📤 WEBHOOK: отправка в канал '{rule.to_whom.title}' (ID: {rule.to_whom.chat_id})")

                    message_text = (f'Пришло сообщение от {caller_id}\n'
                                    f'На номер: {caller_did}\n'
                                    f'Текст: {text}')
                    
                    await tg_bot.send_message(chat_id=rule.to_whom.chat_id, text=message_text)
                    sent_count += 1
                    logger.info(f"✅ WEBHOOK: SMS успешно переслана в канал '{rule.to_whom.title}'")
                    
                except Exception as e:
                    logger.error(f"💥 WEBHOOK: ошибка отправки в канал '{rule.to_whom.title}': {e}")

            logger.info(f"📊 WEBHOOK: отправлено в {sent_count} из {len(matched_rules)} каналов")
                    
            return JsonResponse({
                'status': 'success',
                'message': 'Данные получены и обработаны',
                'rules_count': len(matched_rules),
                'sent_count': sent_count
            }, status=200)
        else:
            logger.info(f"ℹ️ WEBHOOK: для SMS от {caller_id} не найдено подходящих правил")
            return JsonResponse({
                'status': 'success',
                'message': 'Данные получены, но правило не найдено'
            }, status=200)

    except Exception as e:
        logger.error(f"💥 WEBHOOK: критическая ошибка: {e}")
        logger.error(f"💥 WEBHOOK: тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"💥 WEBHOOK: полный traceback:\n{traceback.format_exc()}")
        return JsonResponse({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500) 
