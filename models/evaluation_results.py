from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field
from .individual_response import IndividualResponse


class EvaluationResults(BaseModel):
    data: List[IndividualResponse] = Field(description="Set of question and answer score pairs")