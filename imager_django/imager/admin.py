from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as User_DJ
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from .models import Content, User, Telegram


class TelegramInline(admin.StackedInline):
    model = Telegram
    can_delete = False
    verbose_name_plural = 'telegram'


class TelegramAdmin(BaseUserAdmin):
    inlines = (TelegramInline,)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loader_id', 'type_content', 'moderated')
    list_filter = ('moderated', 'type_content')
    fields = ['media_tag', 'moderated', 'type_content', 'loader_id', 'file_id']
    readonly_fields = ['media_tag', 'type_content', 'loader_id', 'file_id']


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_id', 'tg_name_user', 'tg_username_user',
        'banned', 'last_photo', 'last_video', 'last_voice'
    )
    list_filter = ('banned',)
    fields = [
        'user_id', 'tg_name_user', 'tg_username_user', 'banned',
        'last_photo', 'last_video', 'last_voice'
    ]
    readonly_fields = [
        'user_id', 'tg_name_user', 'tg_username_user',
        'last_photo', 'last_video', 'last_voice'
    ]


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ['action_time', 'user', 'content_type', 'action_flag']
    fields = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    readonly_fields = fields[:]
    ordering = ('-action_time',)


admin.site.register(Content, ContentAdmin)
admin.site.register(User, UserAdmin)
admin.site.site_header = 'Панель бота Илона'

admin.site.unregister(User_DJ)
admin.site.register(User_DJ, TelegramAdmin)

admin.site.register(LogEntry, LogEntryAdmin)
