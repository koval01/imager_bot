from django.db import models


class Content(models.Model):
    CONTENT_TYPE = [
        ('photo', 'Фото'),
        ('video', 'Видео'),
        ('voice', 'Голосовое'),
    ]

    type_content = models.CharField('Тип контента', choices=CONTENT_TYPE, null=False, max_length=5)
    loader_id = models.BigIntegerField('ID юзера', null=False)
    file_id = models.CharField('ID файла', null=False, db_index=True, unique=True, max_length=255, editable=False)
    moderated = models.BooleanField('Проверенный')

    def __str__(self):
        return "%s (Проверенный: %s)" % (self.type_content, self.moderated)

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'


class User(models.Model):
    user_id = models.BigIntegerField("ID юзера", null=False, db_index=True, unique=True)
    banned = models.BooleanField("Забанен")
    last_photo = models.BigIntegerField("ID последнего фото")
    last_video = models.BigIntegerField("ID последнего видео")
    last_voice = models.BigIntegerField("ID последнего голосового")

    def __str__(self):
        return "%s (Забанен: %s)" % (self.user_id, self.banned)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
