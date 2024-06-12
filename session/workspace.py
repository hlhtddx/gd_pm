import logging
from pathlib import Path

from sqlite_utils import Database

from feishu.drive import DriveManager
from utils import debug_level
from utils.config import SqliteConfig
from .common import APP_NAME, global_config, InvalidWorkspaceException, NoLoginError
from .login import Login


class Workspace:
    def __init__(self, path_name: str = '.', create: bool = False):
        if create:
            self.__local_path = Path(path_name).absolute()
        else:
            self.__local_path = self.init_local_path(path_name)
        if not self.__local_path:
            raise InvalidWorkspaceException()
        self.init_config_path()
        self.logger = self.init_logger(filename=self.log_path, level=debug_level)
        self.database = Database(self.db_path)
        self.config = SqliteConfig(database=self.database)
        self.login = self.init_login()
        self.drive = DriveManager(workspace=self, login=self.login)
        self.target_logins = {}
        self.target_drive = None

    @property
    def path(self) -> Path:
        return self.__local_path

    @property
    def config_path(self) -> Path:
        return self.__local_path / APP_NAME

    @property
    def db_path(self) -> Path:
        return self.config_path / 'db.sqlite'

    @property
    def doc_path(self) -> Path:
        return self.config_path / 'object'

    @property
    def log_path(self) -> Path:
        return self.config_path / 'local.log'

    # Initializer for config(local path, tenants info, etc.)
    @staticmethod
    def init_logger(filename, level):
        logger = logging.getLogger("FDA")
        logger.setLevel(level=level)
        handler = logging.FileHandler(filename)
        handler.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def init_local_path(path_name: str) -> Path or None:
        assert path_name
        origin_path = Path(path_name).absolute()
        path = origin_path
        while path != path.anchor and path != Path.home():
            config_path = path / APP_NAME
            if config_path.is_dir():
                return path
            path = path.parent
        return None

    def init_config_path(self) -> None:
        self.config_path.mkdir(exist_ok=True)

    def init_login(self) -> Login or None:
        tenant = global_config.get_tenant(self.config.get('tenant'))
        if tenant:
            return Login(config=self.config, tenant=tenant)
        raise NoLoginError()

    def close(self):
        self.config = None
        self.database.conn.close()

    def login_to_tenant(self, tenant, force):
        if not self.login or tenant != self.login.tenant:
            self.login = Login(self.config, tenant)
            self.config.set('tenant', tenant.name)

        if self.login.login(force):
            pass
            # self.drive.on_login_complete()

    def logout_from_tenant(self, tenant):
        if self.login.logout():
            self.config.set('tenant', '')

    @property
    def is_login(self):
        if not self.login:
            return False
        return self.login.is_login

    def find_file(self, path: Path) -> object or None:
        parent = self.find_file(path.parent)
        if not parent:
            return None
        file_name = path.name
        if file_name.endswith('fdoc_v2'):
            # file is doc
            pass
        return parent.find_child(file_name)
