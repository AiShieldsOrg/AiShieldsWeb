import re
from config import SENSITIVE_DATA_CONFIGS


class SensitiveDataSanitizer:
    def __init__(self) -> None:
        self.sensitive_data = SENSITIVE_DATA_CONFIGS

    def sanitize_input(self, input_content: str) -> str:
        sanitized_content = input_content
        for entity, details in self.sensitive_data.items():
            regex_pattern = details["pattern"]
            placeholder = details["placeholder"]
            sanitized_content = re.sub(regex_pattern, placeholder, sanitized_content, flags=re.IGNORECASE)
        return sanitized_content


