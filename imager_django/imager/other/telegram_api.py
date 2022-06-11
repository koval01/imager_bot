from django.forms.utils import flatatt
from django.utils.html import format_html

import logging as log
import mimetypes
import os
import re

from django.http import HttpResponse
from requests import get as http_get


class Mime:
    def __init__(self, path_or_file: str, default_mime: str = "application/octet-stream") -> None:
        mimetypes.init()
        self.path_or_file = str(path_or_file).lower()
        self.mimetypes = mimetypes
        self.default_mime = default_mime
        self.pattern = re.compile(r"\.[A-z0-9]*$")

    @property
    def extract(self) -> str:
        try:
            return self.mimetypes.types_map[
                re.search(self.pattern, str(self.path_or_file)).group(0)
            ]
        except Exception as e:
            log.info("Error resolve file type. Data: %s; Except: %s" % (self.path_or_file, e))
            return ""

    @property
    def alter_type(self) -> str:
        try:
            content_type = self.extract
            if not content_type:
                raise
            return content_type
        except Exception as e:
            log.debug("MIME detect error! Details: %s" % e)
            return self.default_mime

    def __str__(self) -> str:
        return self.alter_type


class TelegramAPI:
    def __init__(self, file_id: str = None, path: str = None) -> None:
        self.file_id = file_id
        self.path = path

    @property
    def _get_file_data(self) -> dict:
        response = http_get(
            "https://api.telegram.org/bot%s/getFile" % os.getenv("BOT_TOKEN"),
            params={"file_id": self.file_id}
        )
        if 300 > response.status_code >= 200:
            return response.json()["result"]

    @property
    def get_file(self) -> HttpResponse:
        media = http_get(
            'https://api.telegram.org/file/bot%s/%s' % (
                os.getenv("BOT_TOKEN"), self.path
            )
        )
        type_data = Mime(self.path)
        response_data = HttpResponse(
            media.content,
            content_type=type_data,
            status=media.status_code,
            headers={
                "accept-ranges": "bytes"
            }
        )
        return response_data

    def _file_type(self, file_path: str) -> str:
        return "video" if file_path[-3:].lower() in ["mp4", "mov"] else (
            "voice" if file_path[-3:].lower() in ["ogg", "mp3", "oga", "avi"] else "photo"
        )

    def _html_view_build(self, data: dict) -> str:
        _path = "/app/tg_api/%s" % data["path"]
        _video = format_html(
            "<video{} controls muted autoplay><source{}>{}</video>",
            flatatt({"height": "300vh"}),
            flatatt({"src": _path, "type": "video/mp4"}),
            "Ваш браузер не поддерживает видео тег."
        )
        _img = format_html(
            "<img{}/>", flatatt({
                "src": _path, "height": "300vh",
                "onerror": "this.src=\"//http.cat/404\""
            })
        )
        _audio = format_html(
            "<audio{} controls><source{}>{}</audio>",
            flatatt({"height": "300vh"}),
            flatatt({"src": _path, "type": "audio/ogg"}),
            "Ваш браузер не поддерживает аудио элементы."
        )
        return _video \
            if data["type"] == "video" \
            else (_img if data["type"] == "photo" else _audio)

    @property
    def get(self) -> str:
        path = self._get_file_data["file_path"]
        return self._html_view_build({"path": path, "type": self._file_type(path)})

    def __str__(self) -> str:
        return self.get
