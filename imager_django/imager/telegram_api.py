from requests import get as http_get
from django.http import StreamingHttpResponse
import logging as log
import mimetypes
import os
import re


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
    def get_file(self) -> StreamingHttpResponse:
        media = http_get(
            'https://api.telegram.org/file/bot%s/%s' % (
                os.getenv("BOT_TOKEN"), self.path
            ), stream=True
        )
        type_data = Mime(self.path)
        response_data = StreamingHttpResponse(
            media.raw,
            content_type=type_data,
            status=media.status_code,
            headers={
                "accept-ranges": "bytes"
            }
        )
        return response_data

    @property
    def get(self) -> dict:
        path = self._get_file_data["file_path"]
        return {"path": path}
