from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from requests import get as http_get
from .telegram_api import TelegramAPI


def error_load(code: int) -> StreamingHttpResponse:
    resp = http_get("https://http.cat/%d" % code, stream=True)
    return StreamingHttpResponse(resp.raw, content_type=resp.headers.get("content-type"))


@require_GET
@login_required
def get_image(request, file_type, file_name) -> StreamingHttpResponse:
    if file_type == "error":
        return error_load(code=int(file_name[:3]))
    return TelegramAPI(path=f"{file_type}/{file_name}").get_file
