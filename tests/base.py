class BaseTest:
    def setup(self, app, database, test_client):
        self.app = app
        self.db = database
        self.client = test_client
