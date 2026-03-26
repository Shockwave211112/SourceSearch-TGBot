import logging

class SensitiveDataFilter(logging.Filter):
    def __init__(self, sensitive_words: list):
        super().__init__()
        self.sensitive_words = []
        for word in sensitive_words:
            if not word:
                continue
            if hasattr(word, "get_secret_value"):
                self.sensitive_words.append(word.get_secret_value())
            else:
                self.sensitive_words.append(str(word))

    def filter(self, record):
        message = record.getMessage()

        for word in self.sensitive_words:
            if word and word in message:
                message = message.replace(word, "[REDACTED]")

        record.msg = message
        record.args = tuple()
        return True