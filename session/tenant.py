from pathlib import Path

from sqlite_utils import Database

from feishu.auth import Authentication
from utils import logger, debug_level
from feishu.drive import DriveManager


class FileMap(object):
    def __init__(self, tenant, database: Database):
        self.database = database
        self.tenant = tenant
        table_name = f'file_map.{tenant.name}'
        self.table = self.database[table_name]
        if table_name not in self.database.table_names():
            self.table.create({
                'token': str,
                'name': str,
                'p_token': str,
                'parent_path': str,
                'create_time': int,
                'edit_time': int,
                'local_file': str,
            }, pk='token', not_null=('token',))


class FolderIdMap(object):
    def __init__(self, tenant, database):
        self.database = database
        self.tenant = tenant
        table_name = f'folder_id_map.{tenant.name}'
        self.table = self.database[table_name]
        if table_name not in self.database.table_names():
            self.table.create({
                'id': str,
                'name': str,
                'token': str,
                'parent_id': str,
            }, pk='id', not_null=('id',))
