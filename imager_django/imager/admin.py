from django.contrib import admin
from models import Content, User

admin.site.register(Content)
admin.site.register(User)
admin.site.site_header = 'Панель бота Илона ибат'
