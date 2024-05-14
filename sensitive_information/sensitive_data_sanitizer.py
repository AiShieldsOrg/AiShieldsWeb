import re
from sensitive_information.config import SENSITIVE_DATA_CONFIGS
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class SensitiveDataSanitizer:
    def __init__(self) -> None:
        self.sensitive_data = SENSITIVE_DATA_CONFIGS
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def sanitize_input(self, input_content: str) -> str:
        sanitized_content = input_content
        for entity, details in self.sensitive_data.items():
            if entity == "OTHER":
                analysis_results = self.analyzer.analyze(
                    text=sanitized_content,
                    language="en",
                )
                anonymized_results = self.anonymizer.anonymize(
                    text=sanitized_content,
                    analyzer_results=analysis_results
                )
                sanitized_content = anonymized_results.text
            else:
                regex_pattern = details["pattern"]
                placeholder = details["placeholder"]
                sanitized_content = re.sub(regex_pattern, placeholder, sanitized_content, flags=re.IGNORECASE)
        return sanitized_content
