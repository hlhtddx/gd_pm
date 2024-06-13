from typing import Dict

from sqlite_utils import Database
from sqlite_utils.db import NotFoundError

from feishu.base_file import BaseFile
from feishu.folder import Folder
from feishu.media import Media


class DriveDataModel(object):
    def __init__(self, drive, database: Database, table_name: str):
        self.map: Dict[str, BaseFile] = {}
        self.drive = drive
        self.database = database
        self.table_name = table_name
        self.table = self.database[table_name]
        if table_name not in self.database.table_names():
            self._create_table()
        self._create_index()
        self.database.conn.commit()

    def _create_table(self):
        pass

    def _create_index(self):
        pass


class FileMap(DriveDataModel):
    def __init__(self, drive, database: Database):
        super().__init__(drive=drive, database=database, table_name='file_map')
        self.id_map = {}
        self.path_map = {}

    def _create_table(self):
        self.table.create({
            'token': str,
            'name': str,
            'doc_type': str,
            'p_token': str,
            'id': int,
            'parent_id': int,
            'create_time': int,
            'edit_time': int,
            'local_file': str,
        }, pk='token', not_null=('token',))

    def _create_index(self):
        self.table.create_index(columns=('p_token',), if_not_exists=True)
        self.table.create_index(columns=('parent_id',), if_not_exists=True)
        self.table.create_index(columns=('id',), if_not_exists=True)

    def _save_file(self, file):
        # do not save builtin folders
        if file.token == '::virtual_root' or file.p_token == '::virtual_root':
            return True

        self.table.insert({
            'token': file.token,
            'name': file.name,
            'doc_type': file.doc_type,
            'p_token': file.p_token,
            'id': file.id,
            'parent_id': file.parent_id,
            'create_time': file.create_time,
            'edit_time': file.edit_time,
            'local_file': str(file.path),
        }, pk='token', replace=True)
        self.database.conn.commit()
        return True

    def _load_file(self, file_data):
        token = file_data['token']
        name = file_data['name']
        doc_type = file_data['doc_type']
        p_token = file_data['p_token']
        id = file_data['id']
        parent_id = file_data['parent_id']
        create_time = file_data['create_time']
        edit_time = file_data['edit_time']

        if doc_type == 'folder':
            file = Folder(drive=self.drive, token=token, name=name, p_token=p_token, id=id, parent_id=parent_id)
        # elif doc_type == 'doc':
        #     file = Doc(drive=self.drive, token=token, name=name, create_time=create_time, edit_time=edit_time)
        elif doc_type == 'image':
            file = Media(drive=self.drive, token=token, name=name, parent_doc=self.get_item(p_token))
        elif doc_type == 'attachment':
            file = Media(drive=self.drive, token=token, name=name, parent_doc=self.get_item(p_token))
        else:
            return
        self.add_item(file, save_to_db=False)

    def load(self) -> dict:
        sql_query = f'select * from {self.table_name} where doc_type = "folder";'
        for file_data in self.database.query(sql_query):
            self._load_file(file_data=file_data)

        sql_query = f'select * from {self.table_name} where doc_type = "doc";'
        for file_data in self.database.query(sql_query):
            self._load_file(file_data=file_data)

        sql_query = f'select * from {self.table_name} where doc_type <> "folder" and doc_type <> "doc";'
        for file_data in self.database.query(sql_query):
            self._load_file(file_data=file_data)

        self.resolve_parent()
        return self.map

    def get_item(self, token: str) -> BaseFile or None:
        file = self.map.get(token, None)
        if not file:
            return None

        # do not save builtin folders
        if file.token == '::virtual_root' or file.p_token == '::virtual_root':
            return file

        try:
            found = self.table.get(pk_values=token)
        except NotFoundError:
            found = None
        assert found
        if not found:
            self._save_file(file)
        return file

    def add_item(self, file: BaseFile, save_to_db: bool = True) -> bool:
        if save_to_db and not self._save_file(file):
            return False
        self.map[file.token] = file
        if isinstance(file, Folder):
            self.id_map[file.id] = file
            self.path_map[file.path] = file
        return True

    def resolve_parent(self):
        for file in self.map.values():
            file.resolve_parent()
        self._resolve_path()

    def _resolve_path(self):
        for file in self.map.values():
            if file.doc_type == 'folder':
                self.path_map[file.path] = file

    def get_child_folders(self, folder: Folder) -> list[Folder]:
        folders = []
        for file_data in self.table.rows_where(where=f'p_token="{folder.token}"', select='token'):
            folders.append(self.get_item(file_data['token']))
        return folders
#
#
# class DocInFolder(DriveDataModel):
#     def __init__(self, drive, database: Database):
#         super().__init__(drive=drive, database=database, table_name='doc_in_folder_map')
#         self.map = {}
#         self.database = database
#
#     def _create_table(self):
#         self.table.create({
#             'doc_token': str,
#             'folder_token': str,
#         }, pk=('doc_token', 'folder_token'), not_null=('doc_token', 'folder_token'))
#
#     def _create_index(self):
#         self.table.create_index(('folder_token',), if_not_exists=True)
#
#     def reset_folder(self, folder: Folder, docs: list[Doc]) -> bool:
#         if folder.token in self.map:
#             self.map.pop(folder.token)
#         self.table.delete_where('folder_token=?', [folder.token])
#
#         doc_tokens = set()
#         rows = []
#         for doc in docs:
#             doc_tokens.add(doc.token)
#             rows.append({
#                 'doc_token': doc.token,
#                 'folder_token': folder.token,
#             })
#         self.table.insert_all(rows, pk=('doc_token', 'folder_token'))
#         self.database.conn.commit()
#         self.map[folder.token] = doc_tokens
#         return True
#
#     def load(self):
#         for row in self.table.rows:
#             folder_token = row['folder_token']
#             doc_token = row['doc_token']
#             self._add(doc_token, folder_token)
#
#     def add_item(self, doc, folder):
#         self.table.insert(
#             {
#                 'doc_token': doc.token,
#                 'folder_token': folder.token,
#             },
#             pk=('doc_token', 'folder_token'), replace=True)
#         self.database.conn.commit()
#         self._add(doc.token, folder.token)
#
#     def get_folder(self, token):
#         return self.map.get(token, set())
#
#     def _add(self, doc_token: str, folder_token: str):
#         if folder_token in self.map:
#             doc_tokens = self.map[folder_token]
#         else:
#             doc_tokens = set()
#             self.map[folder_token] = doc_tokens
#         doc_tokens.add(doc_token)
#
#
# class PushedFile(DriveDataModel):
#     def __init__(self, drive, database: Database, tenant: str):
#         super().__init__(drive, database, f'pushed_file.{tenant}')
#
#     def _create_table(self):
#         self.table.create({
#             'source_token': str,
#             'target_token': str,
#             'revision': str
#         }, pk='source_token', not_null=('source_token', 'target_token'))
#
#     def _create_index(self):
#         self.table.create_index(('source_token',), if_not_exists=True)
#
#     def load(self):
#         for row in self.table.rows:
#             source_token = row['source_token']
#             target_token = row['target_token']
#             revision = row['revision']
#             self.map[source_token] = (source_token, target_token, revision)
#
#     def add_item(self, file, revision=0):
#         self.database.conn.commit()
#
#     def get_item(self, token):
#         return self.map.get(token, None)
