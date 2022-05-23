from django.urls import path
from . import views

urlpatterns = [
    path('tg_api/<str:file_type>/<str:file_name>', views.get_image, name="custom_page"),
]
