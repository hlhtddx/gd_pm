# from feishu import file_download
# from feishu.auth import LarkCallArguments
# from feishu.file.base_file import BaseFile
#
#
# class File(BaseFile):
#     def __init__(self, login, token, name):
#         super().__init__(login, token, name, 'file')
#
#     @staticmethod
#     def get_instance(tenant, token):
#         if token in tenant.all_file_map:
#             return tenant.all_file_map[token]
#
#         item = File(tenant, token, token)
#         return item
#
#     def get_content(self):
#         data = file_download(self.tenant, LarkCallArguments(), self.token)
#         return data
