from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from .telegram_api import TelegramAPI
import logging as log


class Telegram(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tg_user_id = models.BigIntegerField("Telegram ID")


class Content(models.Model):
    CONTENT_TYPE = [
        ('photo', 'Фото'),
        ('video', 'Видео'),
        ('voice', 'Голосовое'),
    ]

    type_content = models.CharField('Тип контента', choices=CONTENT_TYPE, null=False, max_length=5)
    loader_id = models.BigIntegerField('ID юзера', null=False, help_text="ID пользователя который добавил этот файл")
    file_id = models.CharField(
        'ID файла', null=False, db_index=True, unique=True, max_length=255,
        help_text="ID файла для получения его с сервера Telegram"
    )
    moderated = models.BooleanField(
        'Проверенный', help_text="Если контент отмечен как проверенный, то он попадает пользователям в выдачу."
    )

    def media_tag(self):
        try:
            content = TelegramAPI(str(self.file_id))
        except Exception as e:
            log.debug(e)
            content = None
        return mark_safe(content)

    media_tag.short_description = 'Превью'

    def __str__(self):
        return "%s (Проверенный: %s)" % (self.type_content, self.moderated)

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'


class User(models.Model):
    user_id = models.BigIntegerField("ID юзера", null=False, db_index=True, unique=True)
    banned = models.BooleanField("Забанен", help_text="Забанен ли юзер")
    last_photo = models.BigIntegerField(
        "ID последнего фото", help_text="ID последнего полученного фото"
    )
    last_video = models.BigIntegerField(
        "ID последнего видео", help_text="ID последнего полученного видео"
    )
    last_voice = models.BigIntegerField(
        "ID последнего голосового", help_text="ID последнего полученного голосового сообщения"
    )

    def __str__(self):
        return "%s (Забанен: %s)" % (self.user_id, self.banned)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
