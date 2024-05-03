import threading
from pydoc import text
from typing import Any
from flask import request, jsonify
from database.database import get_database
from sqlalchemy import text

from database.queries import (
    QUERY_SERVICE_PROVIDER_BY_ID,
    QUERY_LLM_RESPONSE_BY_PROVIDER_ID,
    UPDATE_INITIAL_LLM_RESPONSE_STATUS_BY_PROVIDER_ID,
    QUERY_QUESTION_AND_ANSWER_BY_PROVIDER_ID,
    UPDATE_LLM_RESPONSE_STATUS_SUCCESS_BY_PROVIDER_ID,
)
from llm_function.main import evaluate_results

# from server.py
def generate_interview_results(provider_id: int):
    # post_data = request.json
    # provider_id = post_data["provider_id"]

    database = get_database()

    #checks for the service provider available or not
    service_provider_info_by_id = database.execute(
        text(QUERY_SERVICE_PROVIDER_BY_ID),
        {"provider_id": provider_id},
    )

    # Check whether the llm model started evaluating / checks whether there is an entry on the database (result)
    llm_response_by_provider_id = database.execute(
        text(QUERY_LLM_RESPONSE_BY_PROVIDER_ID),
        {"provider_id": provider_id},
    )

    # Service provider has provided answers for the questions, but the LLM hasn't generate the results score yet!
    if (
        llm_response_by_provider_id.rowcount == 0
        and service_provider_info_by_id.rowcount == 1
    ):
        #provider id is taken
        pending_response = llm_response_by_provider_id.fetchall()

        #if provider id is available and the status is processing then return the provider id, status and score
        if len(pending_response) != 0 and pending_response[0][2] == "processing":
            return jsonify(
                results=[
                    {
                        "providerId": pending_response[0][1],
                        "status": pending_response[0][2],
                        "score": pending_response[0][3],
                    }
                ]
            )
        #if the provider id is not presented in llm response then collect all the questions asked and answers given -- check 
        question_answer_list_by_provider_id = database.execute(
            text(QUERY_QUESTION_AND_ANSWER_BY_PROVIDER_ID),
            {"provider_id": provider_id},
        )

        # map the question and answers in dictionary format manner
        results_map_list = [
            {"Id": row[0], "Question": row[2], "Answer": row[3]}
            for row in question_answer_list_by_provider_id
        ]

        #if there is no question and answers then return null result
        if len(results_map_list) == 0:
            database.close()

            return jsonify(results=[])

        # Updating temporarily the status as processing of the LLM model before processing it
        database.execute(
            text(UPDATE_INITIAL_LLM_RESPONSE_STATUS_BY_PROVIDER_ID),
            {"provider_id": provider_id, "status": "processing"},
        )

        database.commit()


        # Handing over the answers to the LLM model - through langchain
        llm_process_thread = threading.Thread(
            target=process_llm_results,
            args=(results_map_list, provider_id), #the thread will run in the background and automatically terminate when the main thread exits.
            daemon=True,
        )

        llm_process_thread.start()
        
        #selecting the exact provider id
        updated_llm_response_by_provider_id = database.execute(
            text(QUERY_LLM_RESPONSE_BY_PROVIDER_ID),
            {"provider_id": provider_id},
        )

        #
        updated_results_map_list = [
            {"providerId": row[1], "status": row[2], "score": row[3]}
            for row in updated_llm_response_by_provider_id
        ]

        database.close()

        #
        return jsonify(results=updated_results_map_list)
    else:
        #map the question asked and answer given in dictionary format for exact service provider
        results_map_list = [
            {"providerId": row[1], "status": row[2], "score": row[3]}
            for row in llm_response_by_provider_id
        ]

        database.close()

        #return in json format
        return jsonify(results=results_map_list)


# The function handled by the thread
def process_llm_results(results_map: list[dict[str, Any]], provider_id: int):
    database = get_database()

    # This function is used to invoke the LLM - through langchain
    llm_response = evaluate_results(results_map)
    score_list = llm_response["scores"]

    # add the total score
    total_score = 0
    for llm_response_data in score_list:
        total_score += llm_response_data["score"]

    #update to datbase
    database.execute(
        text(UPDATE_LLM_RESPONSE_STATUS_SUCCESS_BY_PROVIDER_ID),
        {"score": total_score, "provider_id": provider_id},
    )

    database.commit()
    database.close()

## doubt is what is "results_map" - earlier it was not declared