from database.controller import session_factory
from database.models import Content, User
import logging as log


class LoaderContent:
    def __init__(self, type_content: str, user_id: int) -> None:
        self.session = session_factory()
        self.type_content = type_content
        self.user_id = user_id
