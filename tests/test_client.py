class CustomTestClient:
    def __init__(self, app, reporter):
        self.app = app
        self.reporter = reporter
        self.client = app.test_client()
