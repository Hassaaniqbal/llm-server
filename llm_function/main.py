from typing import List

from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.llms import Ollama

from utils.parsers import get_json_data, json_question_formatter

#return type
response_schemas = [
    ResponseSchema(
        name="scores",
        description="array of scores according to the questions in the following format: [{question: string, answer: string, score: int}]",
        type="array(objects)",
    ),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()

prompt = PromptTemplate(
    template="""
    Evaluate and provide scores for the users' questions and answers as accurately as possible.
    Assign 10 marks for each correct answer. If the answer is incorrect, assign a score of 0.
    If the answer contains no meaningful information or is irrelevant, assign a score of 0.
    If the answer is partially correct or contains some relevant information, assign a score less than 4, based on the degree of accuracy.
    For questions related to experience or those that are open-ended, assess the quality and depth of the response to assign a specific score.
    \n{format_instructions}\n{qna_string}
""",
    input_variables=["qna_string"],
    partial_variables={"format_instructions": format_instructions},
)

model = Ollama(model="llama2")

chain = prompt | model | output_parser


def evaluate_results(json_data: List[dict]):
    qna_string = json_question_formatter(json_data)
    results = chain.invoke({"qna_string": qna_string})
    return results
