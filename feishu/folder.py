import json
import re
from pathlib import Path

from lark_oapi.api.drive.v1 import RequestDoc

from feishu.runner import folder_root_meta, folder_children, get_meta
from feishu.base_file import BaseFile

# from feishu.file.doc import Doc

# ALL_TYPES = ['doc', 'sheet', 'file', 'bitable', 'folder']
ALL_TYPES = ['file', 'sheet', 'folder']
VIRTUAL_ROOT_ID = -1001
SHARED_SPACE_ID = -1002


class FolderMeta:
    def __init__(self, name: str, token: str, id: str, parent_id: str, own_uid: str, create_uid: str, edit_uid: str):
        self.id = id
        self.name = name
        self.token = token
        self.parent_id = parent_id
        self.own_uid = own_uid
        self.create_uid = create_uid
        self.edit_uid = edit_uid


class Folder(BaseFile):
    def __init__(self, drive, token: str, name, parent: BaseFile = None, p_token: str = '', id: int = 0,
                 parent_id: int = 0,
                 meta: FolderMeta or None = None):
        if name:
            _name = name
        elif meta:
            _name = meta.name
        else:
            _name = ''

        if parent:
            p_token = parent.token

        if id:
            self._id = id
        elif meta:
            self._id = meta.id
        else:
            self._id = 0

        if parent_id:
            self._parent_id = parent_id
        elif meta:
            self._parent_id = meta.parent_id
        else:
            self._parent_id = 0

        super().__init__(drive=drive, token=token, name=_name, p_token=p_token, doc_type='folder')
        self._parent = parent

    @property
    def id(self) -> int:
        return self._id

    @property
    def parent_id(self) -> int:
        return self._parent_id

    @property
    def path(self) -> Path:
        if self.parent:
            return self.parent.path / self.normalize_path(self.name)
        else:
            return Path('Unknown')

    @property
    def local_path(self) -> Path:
        return self.drive.path / self.path

    def resolve_parent(self):
        super(Folder, self).resolve_parent()
        # docs = self.drive.doc_in_file_map.get_folder(self.token)
        # for doc in docs:
        #     doc.add_parent(self)

    # @staticmethod
    # def _get_meta(drive, token):
    #     return folder_meta(drive.auth.auth, token)

    @staticmethod
    async def _get_root_meta(drive):
        return await folder_root_meta(drive.auth.auth)

    #
    # def refresh(self):
    #     data = folder_meta(self.drive.auth.auth, self.token)
    #     if data:
    #         self._id = data.id
    #         self._parent_id = data.parent_id
    #         self.set(name=data.name)
    #     return data

    async def refresh_children(self):
        child_files = []
        child_folders = []
        response = await folder_children(self.drive.auth.auth, self.token)
        data = response.data
        if not data:
            return False, [], []

        for item in data.files:
            name = item.name
            token = item.token
            file_type = item.type
            child = self.make_child(name=name, token=token, file_type=file_type)
            if child is None:
                continue

            if child.doc_type == 'folder':
                child_folders.append(child)
            else:
                child_files.append(child)
        self.drive.doc_in_file_map.reset_folder(self, child_files)
        return True, child_folders, child_files

    def get_children(self):
        child_folders = self.drive.get_child_folders(self)
        child_files = self.drive.get_child_doc(self)
        return True, child_folders, child_files

    def set(self, name=None, p_token=None, create_time=0, edit_time=0):
        name_changed = name and name != self._name
        if name_changed:
            self.drive.file_map.path_map.pop(self.path)
        super(Folder, self).set(name=name, p_token=p_token, create_time=create_time, edit_time=edit_time)
        if name_changed:
            self.drive.file_map.path_map[self.path] = self

    def find_child_folder(self, name: str):
        pass

    def make_child(self, name, token, file_type):
        file = self.drive.get_file(token)
        if file:
            file.set(name=name)
            return file

        if file_type == 'folder':
            file = Folder(self.drive, token, name, parent=self)
        # elif file_type == 'doc':
        # file = Doc(self.drive, token, name)
        # file.add_parent(self, True)
        # pass
        elif file_type == 'file':
            pass
        elif file_type == 'sheet':
            pass
        else:
            # Ignore any other types
            return None
        self.drive.add_file(file)
        return file

    def local_child(self, name):
        return None


class VirtualRoot(Folder):
    def __init__(self, drive):
        super().__init__(drive=drive, token='::virtual_root', name='Root', p_token='::virtual_root')

    @property
    def id(self):
        return VIRTUAL_ROOT_ID

    @property
    def parent_id(self):
        return 0

    @property
    def path(self):
        return Path('file')

    def refresh(self):
        return None

    def refresh_children(self):
        if self.drive.auth.is_login:
            return True, [self.drive.shared_space, self.drive.my_space], []
        return False, [], []

    def get_children(self):
        return True, [self.drive.shared_space, self.drive.my_space], []


class MySpace(Folder):
    def __init__(self, drive, parent: VirtualRoot):
        super().__init__(drive=drive, token='', name='MySpace', p_token=parent.token)
        self._parent = parent
        self.import_root = None
        self.import_test_root = None

    @property
    def name(self):
        return self._name

    @property
    def parent_id(self):
        return VIRTUAL_ROOT_ID

    async def on_login_complete(self) -> None:
        # Ensure meta data for root_meta is not same to folder meta
        await self.refresh()
        result, _, _ = self.refresh_children(True)
        if not result:
            return

    async def refresh(self):
        response = await self._get_root_meta(self.drive)
        if response.success():
            data = json.loads(response.raw.content)
            self._token = data['token']
        return self

    def refresh_children(self, show_hidden_folders=False):
        if not self.token:
            return False, [], []
        result, folders, files = super().refresh_children()
        if not show_hidden_folders:
            folders = [x for x in folders if x.name not in ('import_root', 'import_test_root')]
        return result, folders, files


class SharedSpace(Folder):
    PATTERN_URL = re.compile(r'https://\w+.feishu.cn/drive/folder/(\w+)\n?')
    PATTERN_TOKEN = re.compile(r'(\w+)\n?')

    def __init__(self, drive, parent: VirtualRoot):
        super().__init__(drive, token='::shared_space', name='Shared Space', p_token=parent.token)
        self._parent = parent
        self.shared_folders = {}

    @property
    def id(self):
        return SHARED_SPACE_ID

    @property
    def parent_id(self):
        return VIRTUAL_ROOT_ID

    async def load_folders(self, drive):
        folders = {}
        file_path = drive.workspace.config_path / 'shared_folders.txt'
        if file_path.is_file():
            request_docs = []
            with file_path.open('r') as fp:
                for line in fp.readlines():
                    if m := self.PATTERN_URL.match(line):
                        token = m.group(1)
                    elif m := self.PATTERN_TOKEN.match(line):
                        token = m.group(1)
                    else:
                        token = None
                    if token:
                        request_docs.append(RequestDoc.builder().doc_type('folder').doc_token(token).build())
            if len(request_docs) > 0:
                response = await get_meta(self.drive.auth, request_docs)
                data = response.data
                for meta in data.metas:
                    folders[meta.token] = self.make_child(token=meta.token, name=meta.name, file_type='folder')

        return folders

    def refresh(self):
        return None

    async def refresh_children(self):
        return True, list(self.shared_folders.values()), []

    def get_children(self):
        return True, list(self.shared_folders.values()), []

    async def on_login_complete(self):
        await self.refresh_children()
        self.shared_folders = self.load_folders(self.drive)
