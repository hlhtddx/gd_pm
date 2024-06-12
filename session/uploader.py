import json
import os
import sqlite3


class PushDataParser:
    def __init__(self, callback, param):
        self.callback = callback
        self.param = param

    def __parse_dict(self, source_node: dict, target_node: dict):
        type = source_node.get('type', '')
        if type == 'diagram':
            return None

        for key, value in source_node.items():
            if key == 'fileToken':
                new_item = self.callback.replace_token(value)
            else:
                new_item = self.__parse_item(value)
            if new_item is not None:
                target_node[key] = new_item

    def __parse_list(self, source_node: list, target_node: list):
        for item in source_node:
            new_item = self.__parse_item(item)
            if new_item is not None:
                target_node.append(new_item)

    def __parse_item(self, source_item):
        target_item = source_item
        if isinstance(source_item, dict):
            target_item = {}
            self.__parse_dict(source_item, target_item)
        elif isinstance(source_item, list):
            target_item = []
            self.__parse_list(source_item, target_item)
        return target_item

    def parse(self, source: dict):
        return self.__parse_item(source)


class Push:
    def __init__(self, source_root, tenant):
        self.source_root = source_root
        with open(os.path.join(self.source_root, 'source_info.json'), 'r') as fp:
            source_info = json.load(fp)
        self.all_paths = source_info['folders']
        self.all_file = source_info['files']
        self.tenant = tenant
        self.token_map = {}
        self.folder_token_map = {}
        self.db = sqlite3.connect(os.path.join(source_root, f'push-{tenant}.sqlite3'))
        self.init_database()

    def init_database(self):
        cursor = self.db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS token_map (token TEXT PRIMARY KEY, new_token TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS folder_token_map (folder TEXT PRIMARY KEY, new_token TEXT);')
        cursor.close()
        self.db.commit()

        cursor = self.db.cursor()
        for row in cursor.execute('SELECT * from token_map'):
            self.token_map[row[0]] = row[1]

        for row in cursor.execute('SELECT * from folder_token_map'):
            self.folder_token_map[row[0]] = row[1]

    def add_new_token(self, old_token, new_token):
        try:
            cursor = self.db.cursor()
            cursor.execute('INSERT INTO token_map (?, ?);', (old_token, new_token))
            self.db.commit()
            cursor.close()
        except Exception:
            return
        self.token_map[old_token] = new_token

    def prepare_media(self, source_dir):
        return
        with open(os.path.join(source_dir, 'media_list.json'), 'r') as fp:
            media_list = json.load(fp)
        for token in media_list:
            self.push_media(token)

    def prepare_doc_content(self, content):
        source_root = json.loads(content)
        target_root = PushDataParser(self, None).parse(source_root)
        return json.dumps(target_root, ensure_ascii=False)

    def replace_token(self, token):
        return token
        if token not in self.token_map:
            raise 'should not be here'
        return self.token_map[token]

    def push(self):
        authentication.login(self.tenant)
        for doc in self.all_file.values():
            if doc['type'] != 'doc':
                continue
            self.push_doc(doc['token'])

    def ensure_folder(self, folder_path):
        if folder_path in self.folder_token_map:
            return self.folder_token_map[folder_path]
        if folder_path != self.source_root:
            return file_manager.root_meta

        parent_path = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        p_token = self.ensure_folder(parent_path)

        # Create folder and return token
        return file_manager.create_folder(p_token, folder_name)

    def push_doc(self, token):
        # Check if media is uploaded
        if token in self.token_map:
            return self.token_map[token]
        # Check if media is valid
        if token not in self.all_file:
            return None
        file_data = self.all_file[token]
        file_type = file_data['type']
        if file_type != 'doc':
            return None

        file_path = file_data['path']

        folder_path = os.path.dirname(file_path)
        folder_token = self.ensure_folder(folder_path)

        self.prepare_media(file_path)

        file_name = os.path.join(file_path, 'content.json')
        with open(file_name, 'r') as fp:
            content = fp.read()
        new_content = self.prepare_doc_content(content)
        new_token = file_manager.create_doc(folder_token, new_content)
        if new_token is None:
            return None
        self.add_new_token(token, new_token)
        return new_token

    def push_media(self, token):
        # Check if media is uploaded
        if token in self.token_map:
            return self.token_map[token]
        # Check if media is valid
        if token not in self.all_file:
            return None
        file_data = self.all_file[token]
        file_type = file_data['type']
        if file_type == 'png':
            file_name = os.path.join(file_data['path'], file_data['name'])
        elif file_type == 'file':
            file_name = os.path.join(file_data['path'], file_data['name'] + '.bin')
        else:
            return None

        if os.path.getsize(file_name) > 20 * 1024 * 1024:
            raise "File size is over 20M"
        with open(file_name, 'r') as fp:
            content = fp.read()
        new_token = file_manager.upload_media(content)
        if new_token is None:
            return None
        self.add_new_token(token, new_token)
        return new_token


def push(source_dir, target_tenant):
    Push(source_dir, target_tenant).push()
