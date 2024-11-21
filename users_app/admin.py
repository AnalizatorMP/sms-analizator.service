from django.contrib import admin

from users_app.models import User, Key, NumbersService, Rules, TelegramChats


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ('email',)
    search_fields = ('email',)


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'title')
    list_display = ('name', 'user')


@admin.register(NumbersService)
class NumbersServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'telephone')
    search_fields = ('name', 'telephone')


@admin.register(TelegramChats)
class TelegramChatsAdmin(admin.ModelAdmin):
    list_display = ('title', 'chat_id')
    search_fields = ('title', 'chat_id')


@admin.register(Rules)
class RulesAdmin(admin.ModelAdmin):
    list_display = ('from_whom', 'to_whom')
