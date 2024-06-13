import time

from sqlite_utils import Database
from sqlite_utils.db import NotFoundError

from .logger import logger


class SqliteConfig:
    def __init__(self, database:Database=None):
        """Init workspace using an opened database"""
        logger.debug('Init a sqlite config file: %r', database.conn)
        if not database:
            database = Database('data/config.db')
        self.database = database
        self.config = self.database['config']
        if 'config' not in self.database.table_names():
            self.config.create({
                'key': str,
                'value': str,
                'expires': int
            }, pk='key')

    def get(self, key):  # type: (str) -> str
        """
        retrieve a storage key, value from the store, value has an expired time.(unit: second)
        """
        try:
            logger.debug('Get config from sqlite(key=%s)', key)
            values = self.config.get(pk_values=key)
            if 0 < values['expires'] < int(time.time()):
                self.config.delete(pk_values=key)
                return ''
            else:
                return values['value']
        except NotFoundError:
            return ''

    def set(self, key: str, value: str, expire: int = -1):
        """
        storage key, value into the store, value has an expired time.(unit: second)
        """
        logger.debug('Set config to sqlite(key=%s, value=%s, expire=%d)', key, value, expire)
        if expire > 0:
            expire += time.time()
        self.config.insert_all([{'key': key, 'value': value, 'expires': expire}], replace=True)


class ConfigStore:
    def __init__(self, prefix: str, config: SqliteConfig):
        self.prefix = prefix
        self.config = config

    def get(self, key: str):
        value = self.config.get(f'{self.prefix}.{key}')
        if value:
            return True, value
        return False, ''

    def set(self, key: str, value: str, expire: int):
        """
        storage key, value into the store, value has an expiry time.(unit: second)
        """
        self.config.set(f'{self.prefix}.{key}', value, expire)
