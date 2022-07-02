from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as User_DJ
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.utils.translation import ngettext
from django.forms.utils import flatatt
from .models import Content, User, Telegram
from urllib.parse import parse_qs
import logging as log
import json


class MyAdminSite(admin.AdminSite):
    site_url = None


class TelegramInline(admin.StackedInline):
    model = Telegram
    can_delete = False
    verbose_name_plural = 'telegram'


class UserDjangoAdmin(BaseUserAdmin):
    inlines = (TelegramInline,)
    readonly_fields = ("is_superuser",)
    list_display = ("username", "is_staff", "is_active", "last_login")

    def has_change_permission(self, request, obj=None):
        body = parse_qs(request.body.decode("utf-8"))
        if "is_superuser" in body or (obj.is_superuser if obj else None):
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj.is_superuser if obj else None:
            return False
        return True


class ContentAdmin(admin.ModelAdmin):

    @admin.action(description='Отметить как проверенный')
    def make_moderated(self, request, queryset):
        updated = queryset.update(moderated=True)
        self.message_user(request, ngettext(
            '%d элемент контента обозначен как проверенный.',
            '%d элементов контента обозначены как проверенные.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Отметить как НЕпроверенный')
    def make_not_moderated(self, request, queryset):
        updated = queryset.update(moderated=False)
        self.message_user(request, ngettext(
            '%d элемент контента обозначен как НЕпроверенный.',
            '%d элементов контента обозначены как НЕпроверенные.',
            updated,
        ) % updated, messages.SUCCESS)

    def has_add_permission(self, request):
        return False

    list_display = ('id', 'loader_id', 'type_content', 'moderated')
    list_filter = ('moderated', 'type_content')
    
    fields = ['media_tag', 'moderated', 'dislikes', 'type_content', 'loader_id', 'file_id']
    readonly_fields = ['media_tag', 'type_content', 'dislikes', 'loader_id', 'file_id']
    search_fields = ['loader_id', 'file_id']
    
    actions = [make_moderated, make_not_moderated]
    
    list_per_page = 15


class UserAdmin(admin.ModelAdmin):

    @admin.action(description='Забанить (Запрет на загрузку контента)')
    def ban_user(self, request, queryset):
        updated = queryset.update(banned=True)
        self.message_user(request, ngettext(
            '%d пользователь теперь НЕ сможет добавлять контент.',
            '%d пользователей теперь НЕ смогут добавлять контент.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Снять бан (Запрет на загрузку контента)')
    def unban_user(self, request, queryset):
        updated = queryset.update(banned=False)
        self.message_user(request, ngettext(
            '%d пользователь теперь сможет добавлять контент.',
            '%d пользователей теперь смогут добавлять контент.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Забанить (Закрыть доступ)')
    def full_ban_user(self, request, queryset):
        updated = queryset.update(full_banned=True)
        self.message_user(request, ngettext(
            '%d пользователь теперь НЕ сможет пользоваться ботом.',
            '%d пользователей теперь НЕ смогут пользоваться ботом.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Снять бан (Закрыть доступ)')
    def full_unban_user(self, request, queryset):
        updated = queryset.update(full_banned=False)
        self.message_user(request, ngettext(
            '%d пользователь теперь сможет пользоваться ботом.',
            '%d пользователей теперь смогут пользоваться ботом.',
            updated,
        ) % updated, messages.SUCCESS)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def user_link(self, obj):
        author = obj.tg_username_user
        return format_html("<a{}>{}</a>", flatatt({"href": "//t.me/%s" % author}), author) \
            if author != "@Unknown" else author

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        'id', 'user_id', 'tg_name_user', 'user_link',
        'banned', 'full_banned'
    )
    list_filter = ('banned', 'full_banned')
    
    fields = [
        'user_id', 'tg_name_user', 'tg_username_user', 'banned',
        'full_banned', 'last_photo', 'last_video', 'last_voice'
    ]
    search_fields = ['user_id', 'tg_name_user', 'tg_username_user']
    readonly_fields = [
        'user_id', 'tg_name_user', 'tg_username_user',
        'last_photo', 'last_video', 'last_voice'
    ]
    actions = [ban_user, unban_user, full_ban_user, full_unban_user]

    user_link.__name__ = 'Юзернейм пользователя'
    list_per_page = 15


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ['action_time', 'user', 'content_type', 'action_flag']
    fields = [
        'action_time', 'user', 'content_type', 'change_msg',
        'object_repr', 'action_flag', 'object_id'
    ]
    readonly_fields = fields[:]
    ordering = ('-action_time',)

    def change_msg(self, instance):
        json_body = json.loads(instance.change_message)
        try:
            return ",\x20".join([
                f.encode("utf-8").decode("utf-8")
                for f in json_body[0][
                    [i[0] for i in json_body[0].items()][0]
                ]["fields"]
            ])
        except Exception as e:
            log.debug("Error parsing change_message. Details: %s" % e)
            return "N/A"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    change_msg.__name__ = "Задействованные поля"
    list_per_page = 50


admin.site.register(Content, ContentAdmin)
admin.site.register(User, UserAdmin)
admin.site.site_header = 'Imager'
admin.site.site_title = "Панель администратора"

admin.site.unregister(User_DJ)
admin.site.register(User_DJ, UserDjangoAdmin)

admin.site.register(LogEntry, LogEntryAdmin)
