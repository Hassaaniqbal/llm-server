from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_community.llms import Ollama

from models.evaluation_results import EvaluationResults

model = Ollama(model="llama2")

user_query = "joke_query"

parser = JsonOutputParser(pydantic_object=EvaluationResults)

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser

chain.invoke({"query": user_query})