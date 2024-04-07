from langchain_core.pydantic_v1 import BaseModel, Field

class IndividualResponse(BaseModel):
    question: str = Field(description="question asked to the candidate")
    answer: str = Field(description="answer given by the candidate")
    score: int = Field(description="score given by the model based on the answer")