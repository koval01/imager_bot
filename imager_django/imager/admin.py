from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as User_DJ
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
    list_display = ('id', 'user_id', 'banned', 'last_photo', 'last_video', 'last_voice')
    list_filter = ('banned',)
    fields = ['user_id', 'banned', 'last_photo', 'last_video', 'last_voice']
    readonly_fields = ['user_id', 'last_photo', 'last_video', 'last_voice']


admin.site.register(Content, ContentAdmin)
admin.site.register(User, UserAdmin)
admin.site.site_header = 'Панель бота Илона'

admin.site.unregister(User_DJ)
admin.site.register(User_DJ, TelegramAdmin)
