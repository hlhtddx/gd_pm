import attr
from sqlite_utils import Database


@attr.s
class Account:
    open_id = attr.ib(type=str, default='')
    user_id = attr.ib(type=str, default='')
    name = attr.ib(type=str, default='')
    en_name = attr.ib(type=str, default='')


class AccountMap(object):
    def __init__(self, database: Database):
        self.map = {}
        self.database = database
        table_name = f'account'
        self.table = self.database[table_name]
        if table_name not in self.database.table_names():
            self.table.create({
                'open_id': str,
                'user_id': str,
                'name': str,
                'en_name': str,
            }, pk='open_id', not_null=('open_id', 'user_id', 'name'))
            self.database.conn.commit()

    def load(self):
        for row in self.table.rows:
            open_id = row['open_id']
            user_id = row['user_id']
            name = row['name']
            en_name = row['en_name']
            self.map[open_id] = Account(open_id, user_id, name, en_name)

    def add(self, account: Account):
        self.table.insert(
            {
                'open_id': account.open_id,
                'user_id': account.user_id,
                'name': account.name,
                'en_name': account.en_name,
            },
            pk='open_id', replace=True)
        self.database.conn.commit()
        self.map[account.open_id] = account

    def get(self, open_id: str):
        return self.map.get(open_id, None)
