# import json
# from pathlib import Path
#
# from feishu import doc_meta, doc_content, doc_create, user_get
# from feishu.account import Account
# from feishu.file.media import Media
# from feishu.file.base_file import BaseFile
# from utils import logger
#
#
# class Doc(BaseFile):
#     def __init__(self, drive, token, name=None, create_time=0, edit_time=0, meta: DocMetaResult or None = None):
#         name = self.normalize_path(name)
#         if create_time:
#             self._create_time = create_time
#         elif meta:
#             self._create_time = meta.create_time
#         else:
#             self._create_time = 0
#
#         if edit_time:
#             self._edit_time = edit_time
#         elif meta:
#             self._edit_time = meta.edit_time
#         else:
#             self._edit_time = 0
#
#         super().__init__(drive, token, name, 'doc', '')
#         self._parents = []
#         self._p_tokens = []
#
#     def __str__(self):
#         return f'"DOC:{self.name}"\t\ttoken={self.token} type={self.doc_type}'
#
#     @property
#     def create_time(self):
#         return self._create_time
#
#     @property
#     def edit_time(self):
#         return self._edit_time
#
#     @property
#     def path(self):
#         return Path('.fda/objects') / self.token
#
#     @property
#     def info_path(self):
#         return self.path / 'info.json'
#
#     @property
#     def content_path(self):
#         return self.path / 'content.json'
#
#     @property
#     def media_info_path(self):
#         return self.path / 'media_info.json'
#
#     @property
#     def filename(self) -> str:
#         if self.name:
#             return self.name
#         return 'Untitled'
#
#     def resolve_parent(self):
#         return
#
#     def refresh(self):
#         data = doc_meta(self.drive.auth.auth, self.token)
#         if data:
#             self.set(name=data.title, create_time=data.create_time, edit_time=data.edit_time)
#         return data
#
#     def add_parent(self, parent, update_map=False):
#         self._parents.append(parent)
#         if update_map:
#             self.drive.doc_in_file_map.add_item(self, parent)
#
#     @staticmethod
#     def get_instance(drive, token, folder_token=None):
#         if token in drive.all_file_map:
#             return drive.all_file_map[token]
#
#         data = doc_meta(drive.auth.auth, token)
#         if data is None:
#             return None
#
#         item = Doc(drive, token, data.title, meta=data)
#         return item
#
#     def get_content(self):
#         data = doc_content(self.drive.auth.auth, self.token)
#         if data is None:
#             return None
#         return data.content
#
#     def pull(self, to_pull_media) -> bool:
#         try:
#             self.path.mkdir(parents=True, exist_ok=True)
#
#             if self.is_outdated():
#                 content = self.pull_content(to_pull_media=to_pull_media)
#             else:
#                 content = self.content_path.read_text()
#             media_info = []
#             doc_parser = DocParser(json.loads(content))
#             doc_parser.post_pull(parser=Doc.post_pull_parser, param=media_info)
#             self.media_info_path.write_text(json.dumps(media_info, ensure_ascii=False, indent=True))
#             if to_pull_media:
#                 self._pull_media(media_info)
#         except OSError as err:
#             logger.error('Failed to pull doc, err=%s', err)
#             return False
#         return True
#
#     def is_outdated(self) -> bool:
#         if not self.content_path.is_file():
#             return True
#         return self.content_path.stat().st_mtime < self.edit_time
#
#     def pull_content(self, to_pull_media=True) -> str:
#         try:
#             content = self.get_content()
#             self.content_path.write_text(content)
#
#         except Exception as err:
#             logger.error('Failed to get content from doc:%s, err=%s', self.token, err)
#             return ''
#         return content
#
#     def _pull_media(self, media_info):
#         for info in media_info:
#             media_type = info['type']
#             if media_type in ('Person',):
#                 continue
#                 # self._pull_person(info)
#             if media_type == 'ImageItem':
#                 self._pull_image(info)
#             if media_type == 'File':
#                 self._pull_attachment(info)
#
#     def _pull_person(self, info) -> bool:
#         open_id = info['open_id']
#         account = self.drive.account_map.get(open_id)
#         if not account:
#             user_info = user_get(self.drive.auth.auth, open_id, 'open_id')
#             if not user_info:
#                 return False
#             account = Account(open_id=open_id,
#                               user_id=user_info.user.user_id,
#                               name=user_info.user.name,
#                               en_name=user_info.user.en_name)
#             self.drive.account_map.add(account)
#         return True
#
#     def _pull_image(self, info) -> bool:
#         file_token = info['file_token']
#         file_path = self.path / f'{file_token}.png'
#
#         if file_path.is_file() and file_path.stat().st_size > 0:
#             logger.info('Media file %s is already downloaded. Skip it.', file_path)
#             return True
#
#         media = self.drive.get_file(file_token)
#         if not media:
#             media = Media(drive=self.drive, token=file_token, name=file_token, doc_type='doc_image', parent_doc=self)
#         try:
#             content = media.get_content()
#             file_path.write_bytes(content)
#         except Exception as err:
#             logger.error('Failed to get content from doc:%s, err=%s', self.token, err)
#             return False
#         return True
#
#     def _pull_attachment(self, info):
#         file_token = info['file_token']
#         file_name = info['file_name']
#         file_path = self.path / file_name
#
#         if file_path.is_file() and file_path.stat().st_size > 0:
#             logger.info('Media file %s is already downloaded. Skip it.', file_path)
#             return True
#
#         media = self.drive.get_file(file_token)
#         if not media:
#             media = Media(drive=self.drive, token=file_token, name=file_name, doc_type='file', parent_doc=self)
#         try:
#             content = media.get_content()
#             file_path.write_bytes(content)
#         except Exception as err:
#             logger.error('Failed to get content from doc:%s, err=%s', self.token, err)
#             return False
#         return True
#
#     @staticmethod
#     def post_pull_parser(item, param: list):
#         media_info = param
#         if isinstance(item, Person):
#             media_info.append({
#                 'type': 'Person',
#                 'open_id': item.open_id,
#                 'person_name': 'XXX',
#             })
#         if isinstance(item, ImageItem):
#             media_info.append({
#                 'type': 'ImageItem',
#                 'file_token': item.file_token,
#                 'width': item.width,
#                 'height': item.height,
#             })
#         if isinstance(item, File):
#             media_info.append({
#                 'type': 'File',
#                 'file_token': item.file_token,
#                 'view_type': item.view_type,
#                 'file_name': item.file_name,
#             })
#         return DocItem.default_parser(item, Doc.post_pull_parser, param)
#
#     @staticmethod
#     def upload(drive, folder_token, content):
#         if folder_token not in drive.all_file_map:
#             logger.error('Parent dir(token=%s) does not exist', folder_token)
#             return None
#         data = doc_create(drive.auth.auth, folder_token, content)
#         if data is None:
#             return None
#         return Doc.get_instance(drive, data.obj_token)
#
#     @staticmethod
#     def _generate_filename_with_num(name: str, ext: str, number: int):
#         if number == 0:
#             return f'{name}.{ext}'
#         return f'{name} ({number}).{ext}'
#
#     def link_to(self, abs_path: Path):
#         number = 0
#         while True:
#             doc_file_path = abs_path / self._generate_filename_with_num(name=self.name, ext='fdoc_v3', number=number)
#             if doc_file_path.is_file():
#                 try:
#                     doc_info = json.loads(doc_file_path.read_text())
#                     token = doc_info['token']
#                     if token == self.token:
#                         return
#                     else:
#                         number += 1
#                         continue
#                 except Exception as err:
#                     pass
#             doc_info = {
#                 'token': self.token,
#                 'path': str(self.path),
#             }
#             doc_info_json = json.dumps(doc_info)
#             doc_file_path.write_text(doc_info_json)
#             return
