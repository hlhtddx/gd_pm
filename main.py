import asyncio
import os

from backend.app import start_server
from feishu.auth import Authentication
from session.common import Tenant
from session.login import Login
from utils.config import SqliteConfig

config = SqliteConfig()
tenant = Tenant(name='rt', app_id=os.getenv('APP_ID'), app_secret=os.getenv('APP_SECRET'))
login = Login(config, tenant)
# auth = Authentication(login)


async def login_feishu():
    await login.login()


async def main():
    task1 = asyncio.create_task(start_server())
    await asyncio.sleep(1)
    task2 = asyncio.create_task(login_feishu())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())

