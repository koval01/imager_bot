from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from .telegram_api import TelegramAPI


@require_GET
def get_image(request, file_type, file_name) -> StreamingHttpResponse:
    return TelegramAPI(path=f"{file_type}/{file_name}").get_file
