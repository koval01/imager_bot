from django.contrib import admin
from .models import Content, User


class ContentAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'banned', 'last_photo', 'last_video', 'last_voice')
    fields = ('user_id', 'banned', 'last_photo', 'last_video', 'last_voice')
    readonly_fields = ('user_id', 'last_photo', 'last_video', 'last_voice')


admin.site.register(Content, ContentAdmin)
admin.site.register(User)
admin.site.site_header = 'Панель бота Илона ибат'
