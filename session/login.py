from feishu.auth import Authentication
from session.common import Tenant
from utils.config import SqliteConfig, Store


class Login:
    def __init__(self, config: SqliteConfig, tenant: Tenant):
        assert tenant
        self.tenant = tenant
        self.store = Store(prefix=tenant.name, config=config)
        self.config = config
        self.auth = Authentication(login=self)

    def __str__(self):
        return f'Login: tenant={self.tenant.name}, is_login={self.is_login}'

    @property
    def name(self):
        if self.tenant:
            return self.tenant.name
        else:
            return None

    async def login(self, force=False):
        """Check if login. if not, launch login page towards"""
        if not force and await self.auth.check_login():
            return True
        return await self.auth.login()

    def logout(self):
        """Clear access tokens"""
        self.auth.logout()

    async def refresh(self) -> str:
        """Refresh user access token using refresh token"""
        return await self.auth.refresh_token()

    @property
    async def user_access_token(self) -> str:
        return await self.auth.user_access_token

    @property
    async def is_login(self) -> bool:
        return bool(await self.user_access_token)
