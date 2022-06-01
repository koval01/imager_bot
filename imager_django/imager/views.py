from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from requests import get as http_get
from .other.telegram_api import TelegramAPI


def error_load(code: int) -> StreamingHttpResponse:
    resp = http_get("https://http.cat/%d" % code, stream=True)
    return StreamingHttpResponse(resp.raw, content_type=resp.headers.get("content-type"))


@require_GET
@login_required
def get_image(request, file_type, file_name) -> StreamingHttpResponse:
    if file_type == "error":
        return error_load(code=int(file_name[:3]))
    return TelegramAPI(path=f"{file_type}/{file_name}").get_file


def error_400(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=400)


def error_401(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=401)


def error_403(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=403)


def error_404(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=404)


def error_405(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=405)


def error_500(request, exception='Unknown') -> HttpResponse:
    return HttpResponse("", status=500)