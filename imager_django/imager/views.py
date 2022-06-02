from django.http import StreamingHttpResponse, JsonResponse
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


def error_response(request, exception='Unknown', status_code=500) -> JsonResponse:
    return JsonResponse(
        {
            "status_code": status_code, "stamp": hex(int(time() * 1000000)),
            "exception": exception
        }, status=status_code
    )

error_400 = lambda r, e: error_response(r, e, 400)
error_401 = lambda r, e: error_response(r, e, 401)
error_403 = lambda r, e: error_response(r, e, 403)
error_404 = lambda r, e: error_response(r, e, 404)
error_405 = lambda r, e: error_response(r, e, 405)
error_500 = lambda r, e: error_response(r, e, 500)