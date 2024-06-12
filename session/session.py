from session.login import Login


class Session(object):
    def __init__(self, workspace, tenant):
        self.workspace = workspace
        self.logger = workspace.logger
        self.config = workspace.config
        self.login = Login(config=self.config, tenant=tenant)
        self.drive = workspace.drive

    def login(self, force):
        self.login.login(force)

    def logout(self):
        self.login.logout()

    @property
    def is_login(self):
        if not self.login:
            return False
        return self.login.is_login
