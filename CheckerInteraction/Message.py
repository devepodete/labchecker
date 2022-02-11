class Message:
    def __init__(self, message: str, error_occurred=False, args=None):
        self.message = message
        self.error_occurred = error_occurred
        self.args = args
