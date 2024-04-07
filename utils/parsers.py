import json
from typing import List

def get_json_data(json_file_path: str):
    json_file = open(json_file_path)
    json_data = json.load(json_file)
    return json_data

def json_question_formatter(json_object_list: List[dict]):
    return '\n\n'.join(list(map(lambda data: f'Question {data['Id']}: {data['Question']}\nAnswer: {data['Answer'] if data['Answer'] != '' else 'Unknown'}', json_object_list)))