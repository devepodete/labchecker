class Message:
    def __init__(self, error_occurred: bool, message: str, args=None):
        self.error_occurred = error_occurred
        self.message = message
        self.args = args
