import re
from pathlib import Path


class BaseFile(object):
    def __init__(self, drive, token: str, name: str, doc_type: str, p_token: str):
        self.drive = drive
        self._token = token
        self._name = self.normalize_path(name)
        self._doc_type = doc_type
        self._p_token = p_token
        self._parent = None
        self._create_time = 0
        self._edit_time = 0

    def __str__(self):
        return f'Name:"{self.name}"\tType={self.doc_type}, Token={self.token}'

    def get_content(self):
        return None

    @property
    def token(self) -> str:
        return self._token

    @property
    def name(self) -> str:
        return self.normalize_path(self._name)

    @property
    def doc_type(self) -> str:
        return self._doc_type

    @property
    def p_token(self) -> str:
        return self._p_token

    @property
    def id(self) -> int:
        return 0

    @property
    def parent_id(self) -> int:
        return 0

    @property
    def create_time(self) -> int:
        return 0

    @property
    def edit_time(self) -> int:
        return 0

    @property
    def parent(self):
        if isinstance(self._parent, str):
            return None
        return self._parent

    @property
    def path(self) -> Path:
        return Path('')

    def on_changed(self):
        self.drive.file_map.add_item(self)

    def set(self, name=None, p_token=None, create_time=0, edit_time=0):
        changed = False

        if name and name != self._name:
            self._name = self.normalize_path(name)
            changed = True

        if p_token and p_token != self._p_token:
            self._p_token = p_token
            changed = True

        if create_time and create_time != self._create_time:
            self._create_time = create_time
            changed = True

        if edit_time and edit_time != self._edit_time:
            self._edit_time = edit_time
            changed = True

        if changed > 0:
            self.on_changed()

    def resolve_parent(self):
        self._parent = self.drive.get_file(self._p_token)
        assert self._parent

    def remote_child(self, name):
        pass

    def local_child(self, name):
        pass

    @staticmethod
    def normalize_path(name: str) -> str:
        name = re.sub(r'[\\/|*?]', '_', name)
        return name
