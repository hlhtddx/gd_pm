from pathlib import Path

from sqlite_utils import Database

from utils import logger
from utils.config_store import SqliteConfig

APP_NAME = 'gd-pm'


class InvalidWorkspaceException(Exception):
    pass


class NoLoginException(Exception):
    pass


class PermissionException(Exception):
    pass


class InvalidArgumentException(Exception):
    pass


class NoLoginError(Exception):
    pass


class Tenant:
    __local_path: Path

    def __init__(self, name: str, app_id: str, app_secret: str):  # type (str, str, str) -> None
        self.name = name
        self.app_id = app_id
        self.app_secret = app_secret

    def __str__(self):
        return f'tenant: name={self.name}, app_id={self.app_id} app_secret={self.app_secret}'

    def __eq__(self, other):
        if not other:
            return False
        return self.name == other.name

#
# class GlobalConfig(SqliteConfig):
#     PATH = Path.home() / '.config' / APP_NAME
#     CONFIG_DB_PATH = PATH / 'config.db'
#     CONFIG_JS_PATH = PATH / 'config.json'
#
#     try:
#         PATH.mkdir(parents=True, exist_ok=True)
#     except OSError as err:
#         raise err
#
#     def __init__(self):
#         super().__init__(Database(GlobalConfig.CONFIG_DB_PATH))
#         # super().__init__(GlobalConfig.CONFIG_JS_PATH)
#         self.tenants = self.init_tenants()
#
#     def init_tenants(self):
#         tenants = {}
#         tenant_ids_str = self.get('tenants')
#         if not tenant_ids_str:
#             return tenants
#         tenant_ids = tenant_ids_str.split(',')
#         for tenant_id in tenant_ids:
#             app_id = self.get(f'APP_ID.{tenant_id}')
#             app_secret = self.get(f'APP_SECRET.{tenant_id}')
#             if not app_id or not app_secret:
#                 logger.warn('APP_ID or APP_SECRET is not stored for tenant:%s', tenant_id)
#                 continue
#             tenants[tenant_id] = Tenant(name=tenant_id, app_id=app_id, app_secret=app_secret)
#         return tenants
#
#     def get_tenant(self, tenant_name) -> Tenant or None:
#         if tenant_name not in self.tenants:
#             return None
#         return self.tenants[tenant_name]
#
#     def set_tenant(self, tenant_name, app_id, app_secret) -> Tenant:
#         if tenant_name not in self.tenants:
#             tenant = Tenant(name=tenant_name, app_id=app_id, app_secret=app_secret)
#             self.tenants[tenant_name] = tenant
#         else:
#             tenant = self.tenants[tenant_name]
#             tenant.app_id = app_id
#             tenant.app_secret = app_secret
#         self._store_tenants()
#         return tenant
#
#     def delete_tenant(self, tenant_name) -> Tenant or None:
#         if tenant_name not in self.tenants:
#             return False
#         self.tenants.pop(tenant_name)
#         self._store_tenants()
#         return True
#
#     def _store_tenants(self):
#         for name, tenant in self.tenants.items():
#             self.set(f'APP_ID.{name}', tenant.app_id)
#             self.set(f'APP_SECRET.{name}', tenant.app_secret)
#         self.set('tenants', ','.join(self.tenants.keys()))
#         self.database.conn.commit()
#
#
# global_config = GlobalConfig()
