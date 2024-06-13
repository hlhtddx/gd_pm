import asyncio
import time
import webbrowser
from typing import Dict
from urllib.parse import urlencode

from lark_oapi.api.authen.v1 import (
    CreateOidcAccessTokenRequestBodyBuilder,
    CreateOidcAccessTokenRequestBuilder,
    CreateOidcRefreshAccessTokenRequestBodyBuilder,
    CreateOidcRefreshAccessTokenRequestBuilder,
    CreateOidcRefreshAccessTokenResponse,
    CreateAccessTokenResponseBody,
    CreateOidcRefreshAccessTokenResponseBody
)

from feishu.client import client
from utils import logger, Settings
from utils.config_store import ConfigStore

if Settings.DEBUG:
    REFRESH_INTERVAL = 30
else:
    REFRESH_INTERVAL = 600


class Authentication:
    auth_queue: Dict[str, 'Authentication'] = {}

    def __init__(self, tenant, config):
        self.tenant = tenant
        self.config = config
        self.store = ConfigStore(prefix=tenant, config=config)
        self.code_returned = ''
        self._access_token: str = ''
        self._expires_in: int = -1
        self.event = asyncio.Event()

    @property
    def is_login(self):
        return self._access_token and self._expires_in > time.time()

    def _store_user_access_token(
            self,
            user_token_info: CreateAccessTokenResponseBody | CreateOidcRefreshAccessTokenResponseBody
    ) -> None:
        """ConfigStore access token to config store"""
        self.store.set('user_access_token', user_token_info.access_token, user_token_info.expires_in)
        self.store.set('refresh_token', user_token_info.refresh_token, user_token_info.refresh_expires_in)
        self.schedule_refresh_task = asyncio.create_task(self.timer_to_refresh_token(user_token_info.expires_in - 1800))
        self._access_token = user_token_info.access_token
        self._expires_in = user_token_info.refresh_expires_in + time.time()

    async def _retrieve_token(self, code) -> bool:
        """Retrieve access token from challenge code"""
        body = CreateOidcAccessTokenRequestBodyBuilder().code(code).grant_type('authorization_code').build()
        request = CreateOidcAccessTokenRequestBuilder().request_body(body).build()
        response = await client.authen.v1.oidc_access_token.acreate(request)
        if response.code == 0:
            logger.info('Get access token:%s', response.data)
            self._store_user_access_token(response.data)
            return True
        logger.error('error error:%s, msg:%s', response.code, response.msg)
        return False

    async def wait_for_login(self):
        self.auth_queue[self.tenant.name] = self
        logger.info('Wait for auth')
        await self.event.wait()
        logger.info('Wait for auth done')

    @staticmethod
    def on_login_success(name, code):
        """Retrieve access token from challenge code"""
        auth: Authentication = Authentication.auth_queue.get(name)
        if not auth:
            logger.error('No queued auth session found')
            return
        auth.code_returned = code
        logger.info('Set event for auth, code=%s', code)
        auth.event.set()

    async def _launch_login_url(self) -> None:
        redirect_uri = 'https://dev.hlhtddx.net:15196/feishu/login_success'
        # scope = 'docs:doc:readonly'
        param = urlencode({'redirect_uri': redirect_uri, 'app_id': self.tenant.app_id, 'state': self.tenant.name})
        self.event.clear()
        login_uri = '''https://open.feishu.cn/open-apis/authen/v1/authorize?''' + param
        webbrowser.open_new_tab(login_uri)
        await self.wait_for_login()

    @property
    async def user_access_token(self) -> str:
        result, user_access_token = self.store.get('user_access_token')
        if result and user_access_token:
            return user_access_token

        user_access_token = await self.refresh_token()
        if user_access_token:
            return user_access_token

        return ''

    async def login(self) -> bool:
        self.code_returned = ''
        await self._launch_login_url()
        if self.code_returned:
            logger.info('Get code')
            await self._retrieve_token(self.code_returned)
            logger.info('auth done')
        return self.is_login

    def logout(self) -> None:
        self.store.set('user_access_token', '', -1)
        self.store.set('refresh_token', '', -1)

    async def check_login(self) -> bool:
        return await self.refresh_token() != ''

    async def refresh_token(self) -> str:
        """Refresh access token"""
        logger.debug('To refresh token')
        result, refresh_token = self.store.get('refresh_token')
        if not refresh_token:
            return ''

        body = CreateOidcRefreshAccessTokenRequestBodyBuilder().refresh_token(refresh_token).build()
        req = CreateOidcRefreshAccessTokenRequestBuilder().request_body(body).build()
        resp: CreateOidcRefreshAccessTokenResponse = await client.authen.v1.oidc_refresh_access_token.acreate(req)
        if resp.code == 0:
            self._store_user_access_token(resp.data)
            return resp.data.access_token
        else:
            logger.error('error error:%s, msg:%s', resp.code, resp.msg)
            return ''

    async def timer_to_refresh_token(self, elapsed_time):
        end = time.time() + elapsed_time
        while time.time() < end:
            logger.debug('Slept for %d s', REFRESH_INTERVAL)
            await asyncio.sleep(REFRESH_INTERVAL)
        await self.refresh_token()
