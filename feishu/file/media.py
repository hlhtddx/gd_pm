from pathlib import Path

from feishu import media_download, media_upload_all
from .base_file import BaseFile


class Media(BaseFile):
    def __init__(self, drive, token, name, parent_doc = None, doc_type='doc_image'):
        super().__init__(drive=drive, token=token, name=name, p_token=parent_doc.token, doc_type=doc_type)
        self._parent = parent_doc

    @staticmethod
    def get_instance(drive, token, name, parent):
        if token in drive.all_file_map:
            return drive.all_file_map[token]

        item = Media(drive, token, name, parent)
        return item

    def get_content(self):
        return media_download(self.drive.login.auth, self.token)

    @staticmethod
    def upload(drive, doc, local_file_path, doc_type='doc_image'):
        p = Path(local_file_path)
        file_name = p.name
        file_size = p.stat().st_size
        with p.open(mode='rb') as file_fp:
            data = media_upload_all(drive.login.auth, file_name, doc_type, doc.token, file_size, file_fp)
            if not data:
                return None
        return Media.get_instance(drive, token=data.file_token, name=file_name, parent=doc)

    def download(self, target_dir: str) -> bool:
        target_path = Path(target_dir)
        if not target_path.is_dir():
            return False
        target_path /= self.token + '.bin'
        content = self.get_content()
        if not content:
            return False
        target_path.write_bytes(content)
