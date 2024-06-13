from functools import wraps

from lark_oapi import BaseResponse, BaseRequest, HttpMethod, AccessTokenType
from lark_oapi.api.drive.v1 import ListFileResponse, ListFileRequest, BatchQueryMetaRequest, MetaRequest, \
    BatchQueryMetaResponse, DownloadFileRequest, DownloadFileResponse, DownloadMediaRequest, DownloadMediaResponse

from utils import logger
from feishu.client import client
from .auth import Authentication

ERR_CODE_TOKEN_EXPIRED = 99991677
RETRY_TIMES = 3


class LarkCallArguments:
    auth: Authentication or None

    def __init__(self, auth):
        self.auth = auth
        self.config = None
        self.user_access_token = None
        self.service = None


def lark_call(service_factory, uses_user_token=True):
    def outer(func):
        @wraps(func)
        def inner(auth, *args, **kargs):
            largs = LarkCallArguments(auth)
            largs.config = auth.config
            largs.user_access_token = auth.user_access_token if uses_user_token else None
            largs.service = service_factory(largs.config)

            for retry_count in range(RETRY_TIMES):
                if uses_user_token and not largs.user_access_token and not auth.auth():
                    auth.is_login = False
                    return None

                resp = None
                try:
                    resp = func(largs, *args, **kargs)
                except Exception as err:
                    logger.error('Auth Error, %s', err)

                if resp is None:
                    logger.error('Unknown error without response')
                    return None

                if uses_user_token and resp.code == ERR_CODE_TOKEN_EXPIRED:
                    logger.warn('Token expired code=%d, msg=%s', resp.code, resp.msg)
                    largs.user_access_token = auth.refresh_token()
                    continue
                elif resp.code != 0:
                    logger.error('Failed to execute func, code=%d, msg=%s', resp.code, resp.msg)
                    return None

                auth.is_login = True
                return resp.data
            return None

        return inner

    return outer


# @lark_call(DriveExplorerService)
async def folder_root_meta(args) -> BaseResponse:
    request: BaseRequest = BaseRequest.builder() \
        .http_method(HttpMethod.GET) \
        .uri("/open-apis/drive/explorer/v2/root_folder/meta") \
        .headers(dict(Authorization=args.user_access_token)) \
        .token_types({AccessTokenType.USER}) \
        .build()
    return await client.arequest(request)


async def folder_children(args, token) -> ListFileResponse:
    request: ListFileRequest = ListFileRequest.builder() \
        .page_size(200) \
        .folder_token(token) \
        .order_by("EditedTime") \
        .direction("DESC") \
        .user_id_type("user_id") \
        .build()

    response: ListFileResponse = await client.drive.v1.file.alist(request)
    return response


async def get_meta(args, request_docs) -> BatchQueryMetaResponse:
    request: BatchQueryMetaRequest = BatchQueryMetaRequest.builder() \
        .user_id_type("user_id") \
        .request_body(MetaRequest.builder()
                      .request_docs(request_docs)
                      .with_url(True)
                      .build()) \
        .build()

    # 发起请求
    response: BatchQueryMetaResponse = await client.drive.v1.meta.abatch_query(request)
    return response


async def file_download(args, token) -> DownloadFileResponse:
    request: DownloadFileRequest = DownloadFileRequest.builder() \
        .file_token(token) \
        .build()
    response: DownloadFileResponse = await client.drive.v1.file.adownload(request)
    return response


async def media_download(args, token) -> DownloadMediaResponse:
    request: DownloadMediaRequest = DownloadMediaRequest.builder() \
        .file_token(token) \
        .build()
    response: DownloadMediaResponse = await client.drive.v1.media.adownload(request)
    return response
