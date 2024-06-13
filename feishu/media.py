from pathlib import Path

from .base_file import BaseFile
from .runner import media_download


class Media(BaseFile):
    def __init__(self, drive, token, name, parent_doc=None, doc_type='doc_image'):
        super().__init__(drive=drive, token=token, name=name, p_token=parent_doc.token, doc_type=doc_type)
        self._parent = parent_doc

    @staticmethod
    def get_instance(drive, token, name, parent):
        if token in drive.all_file_map:
            return drive.all_file_map[token]

        item = Media(drive, token, name, parent)
        return item

    def get_content(self):
        return media_download(self.drive.auth.auth, self.token)

    def download(self, target_dir: str) -> bool:
        target_path = Path(target_dir)
        if not target_path.is_dir():
            return False
        target_path /= self.token + '.blob'
        content = self.get_content()
        if not content:
            return False
        target_path.write_bytes(content)
