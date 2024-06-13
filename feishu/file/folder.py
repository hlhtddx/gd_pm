import re
from pathlib import Path

from feishu import folder_root_meta, folder_meta, folder_children, folder_create
from feishu.file.base_file import BaseFile
from feishu.file.doc import Doc
from utils import logger

# ALL_TYPES = ['doc', 'sheet', 'file', 'bitable', 'folder']
ALL_TYPES = ['doc', 'folder']
VIRTUAL_ROOT_ID = -1001
SHARED_SPACE_ID = -1002


class Folder(BaseFile):
    def __init__(self, drive, token: str, name, parent: BaseFile = None, p_token: str = '', id: int = 0,
                 parent_id: int = 0,
                 meta: FolderMetaResult or None = None):
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
        docs = self.drive.doc_in_file_map.get_folder(self.token)
        for doc in docs:
            doc.add_parent(self)

    @staticmethod
    def _get_meta(drive, token):
        return folder_meta(drive.login.auth, token)

    @staticmethod
    def _get_root_meta(drive):
        return folder_root_meta(drive.login.auth)

    def refresh(self):
        data = folder_meta(self.drive.login.auth, self.token)
        if data:
            self._id = data.id
            self._parent_id = data.parent_id
            self.set(name=data.name)
        return data

    def refresh_children(self):
        child_files = []
        child_folders = []
        data = folder_children(self.drive.login.auth, self.token)
        if not data:
            return False, [], []
        if data.children is None:
            return True, [], []

        for item in data.children.values():
            name = item['name']
            token = item['token']
            file_type = item['type']
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

    def create_sub_folder(self, name):
        body = FolderCreateReqBody(name)
        data = folder_create(self.drive.login.auth, body, self.token)
        if not data:
            return None
        token = data.token
        return self.make_child(token, name, 'folder')

    def make_child(self, name, token, file_type):
        file = self.drive.get_file(token)
        if file:
            file.set(name=name)
            return file

        if file_type == 'folder':
            file = Folder(self.drive, token, name, parent=self)
        elif file_type == 'doc':
            file = Doc(self.drive, token, name)
            file.add_parent(self, True)
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
        return Path('.')

    def refresh(self):
        return None

    def refresh_children(self):
        if self.drive.login.is_login:
            return True, [self.drive.shared_space, self.drive.my_space], []
        return False, [], []

    def get_children(self):
        return True, [self.drive.shared_space, self.drive.my_space], []


class MySpace(Folder):
    def __init__(self, drive, parent: VirtualRoot):
        root_meta = MySpace._get_root_meta(drive)
        if not root_meta:
            raise ConnectionError()
        super().__init__(drive=drive, token=root_meta.token, name='MySpace', p_token=parent.token)
        self._parent = parent
        self.import_root = None
        self.import_test_root = None

    @property
    def name(self):
        return self._name

    @property
    def parent_id(self):
        return VIRTUAL_ROOT_ID

    def on_login_complete(self) -> None:
        # Ensure meta data for root_meta is not same to folder meta
        self.refresh()
        result, folders, files = self.refresh_children(True)
        if not result:
            return
        founded = 0
        for folder in folders:
            if folder.name == 'import_root':
                self.import_root = folder
                founded += 1
            elif folder.name == 'import_test_root':
                self.import_test_root = folder
                founded += 1
            if founded == 2:
                break
        else:
            self.ensure_import_target()

    def refresh(self):
        return self

    def refresh_children(self, show_hidden_folders=False):
        result, folders, files = super().refresh_children()
        if not show_hidden_folders:
            folders = [x for x in folders if x.name not in ('import_root', 'import_test_root')]
        return result, folders, files

    def ensure_import_target(self):
        if not self.import_root:
            self.import_root = self.create_sub_folder('import_root')
        if not self.import_test_root:
            self.import_test_root = self.create_sub_folder('import_test_root')
        return self


class SharedSpace(Folder):
    PATTERN_URL = re.compile(r'https://\w+.feishu.cn/drive/folder/(\w+)\n?')
    PATTERN_TOKEN = re.compile(r'(\w+)\n?')

    def __init__(self, drive, parent: VirtualRoot):
        super().__init__(drive, token='::shared_space', name='Shared Space', p_token=parent.token)
        self._parent = parent
        self.shared_folders = self.load_folders(drive)

    @property
    def id(self):
        return SHARED_SPACE_ID

    @property
    def parent_id(self):
        return VIRTUAL_ROOT_ID

    def load_folders(self, drive):
        folders = {}
        file_path = drive.workspace.config_path / 'shared_folders.txt'
        if file_path.is_file():
            with file_path.open('r') as fp:
                for line in fp.readlines():
                    token = None
                    m = self.PATTERN_URL.match(line)
                    if m:
                        token = m.group(1)
                    else:
                        m = self.PATTERN_TOKEN.match(line)
                        if m:
                            token = m.group(1)
                    if token:
                        meta = self._get_meta(self.drive, token=token)
                        folders[token] = self.make_child(token=token, name=meta.name, file_type='folder')

        return folders

    def refresh(self):
        return None

    def refresh_children(self):
        return True, list(self.shared_folders.values()), []

    def get_children(self):
        return True, list(self.shared_folders.values()), []

    def on_login_complete(self):
        self.refresh_children()
