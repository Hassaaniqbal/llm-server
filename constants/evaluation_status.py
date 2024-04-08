from enum import StrEnum

class EvaluationStatus(StrEnum):
    PROCESSING = "processing",
    SUCCESS = "success",
    FAILURE = "failure"