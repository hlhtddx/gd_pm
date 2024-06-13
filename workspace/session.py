# from feishu.auth import Authentication
#
#
# class Session(object):
#     def __init__(self, workspace, tenant):
#         self.workspace = workspace
#         self.logger = workspace.logger
#         self.config = workspace.config
#         self.auth = Authentication(config=self.config, tenant=tenant)
#         self.drive = workspace.drive
#
#     async def login(self, force):
#         if not force and await self.auth.check_login():
#             return True
#         return await self.auth.login()
#
#     def logout(self):
#         self.auth.logout()
#
#     @property
#     def is_login(self):
#         return self.auth.is_login
