SENSITIVE_DATA_CONFIGS = {
    "EMAIL": {
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "placeholder": "<EMAIL_ADDRESS>"
    },
    "CREDIT_CARD": {
        "pattern": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "placeholder": "<CREDIT_CARD>"
    },
    "US_SSN": {
        "pattern": r"\b(?!\d{9}$)\d{3}-?\d{2}-?\d{4}\b",
        "placeholder": "<US_SSN>"
    },
    "US_BANK_ACCOUNT": {
        "pattern": r"\b\d{9}\b",
        "placeholder": "<US_BANK_ACCOUNT>"
    },
    "PHONE_NUMBER": {
        "pattern": r"\b\d{3}-?\d{3}-?\d{4}\b",
        "placeholder": "<PHONE_NUMBER>"
    },
    "IP_ADDRESS": {
        "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "placeholder": "<IP_ADDRESS>"
    },
    "UUID": {
        "pattern": r"\b[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\b",
        "placeholder": "<UUID>"
    },
    "US_DRIVING_LICENSE": {
        "pattern": r"\b[A-Z]{1,2}\d{4,8}\b",
        "placeholder": "<US_DRIVING_LICENSE>"
    },
    "IBAN_CODE": {
        "pattern": r"\b[A-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{14}\b",
        "placeholder": "<IBAN_CODE>"
    },
    "OTHER": {
        "pattern": r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b",
        "placeholder": ""
    }
}