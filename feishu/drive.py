from pathlib import Path

from utils import logger
from workspace.drive_model import FileMap
# from .account import AccountMap
from .base_file import BaseFile
from .folder import Folder, MySpace, SharedSpace, VirtualRoot


class DriveManager:
    virtual_root: VirtualRoot
    shared_space: SharedSpace
    my_space: Folder or None

    def __init__(self, workspace, auth):
        self.workspace = workspace
        self.path = workspace.path
        self.auth = auth

        # self.account_map = AccountMap(database=workspace.database)
        # self.doc_in_file_map = DocInFolder(drive=self, database=workspace.database)
        self.file_map = FileMap(drive=self, database=workspace.database)

        self.virtual_root = VirtualRoot(drive=self)
        self.shared_space = SharedSpace(drive=self, parent=self.virtual_root)
        self.my_space = MySpace(drive=self, parent=self.virtual_root)

        self.add_file(self.virtual_root, save_to_db=False)
        self.add_file(self.shared_space, save_to_db=False)
        self.add_file(self.my_space, save_to_db=False)

        self._init_file_maps()

    def _init_file_maps(self):
        # self.account_map.load()
        self.file_map.load()

    async def on_login_complete(self):
        await self.my_space.on_login_complete()
        await self.shared_space.on_login_complete()

    def get_meta(self, token=''):
        item = self.get_file(token)  # if token else self.current_folder
        if item is None:
            return None
        return item.refresh()

    def add_file(self, file, save_to_db: bool = True) -> None:
        self.file_map.add_item(file, save_to_db)

    def get_file(self, token) -> BaseFile or None:
        return self.file_map.get_item(token)

    def find_file_by_path(self, folder_path: Path) -> BaseFile or None:
        return self.file_map.path_map.get(folder_path, None)

    def get_child_folders(self, folder: Folder) -> list[Folder]:
        return self.file_map.get_child_folders(folder)

    #
    # def get_child_doc(self, folder: Folder) -> list[Doc]:
    #     doc_tokens = self.doc_in_file_map.get_folder(folder.token)
    #     docs = [self.file_map.get_item(token) for token in doc_tokens]
    #     return docs

    # Lark Drive Low-level Operations
    def download(self, token: str, target_dir: str):
        item = self.get_file(token)
        if item is None:
            logger.error('No file with token=%s', token)
            return None

        content = item.download(target_dir)
        return content

    # def create_folder(self, p_token, name):
    #     parent_folder = self.file_map.get_item(p_token)
    #     if parent_folder is None:
    #         logger.error('Parent folder(%s) does not exist or not loaded yet', p_token)
    #         return None
    #     if parent_folder.doc_type != 'folder':
    #         logger.error('Parent (%s) has wrong type. folder is MUST', p_token)
    #         return None
    #     return parent_folder.create_sub_folder(name)
    #
    # def upload_doc(self, local_file_path, p_token=''):
    #     if not p_token:
    #         p_token = self.my_space.import_test_root.token
    #     try:
    #         content = Path(local_file_path).read_text()
    #     except FileNotFoundError as fnf_error:
    #         logger.error(fnf_error.strerror)
    #         return None
    #     return Doc.upload(self, p_token, content)
    #
    # def upload_media(self, doc_token, local_file_path, doc_type):
    #     doc = self.file_map.get_item(doc_token)
    #     if not doc:
    #         logger.error('Parent doc(%s) does not exist or not loaded yet', doc_token)
    #         return None
    #     return Media.upload(self, doc, local_file_path, doc_type)
