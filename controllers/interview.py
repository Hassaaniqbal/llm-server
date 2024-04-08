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


def generate_interview_results(provider_id: int):
    post_data = request.json
    provider_id = post_data["provider_id"]

    database = get_database()

    service_provider_info_by_id = database.execute(
        text(QUERY_SERVICE_PROVIDER_BY_ID),
        {"provider_id": provider_id},
    )

    # Check whether the llm model started evaluating
    llm_response_by_provider_id = database.execute(
        text(QUERY_LLM_RESPONSE_BY_PROVIDER_ID),
        {"provider_id": provider_id},
    )

    if (
        llm_response_by_provider_id.rowcount == 0
        and service_provider_info_by_id.rowcount == 1
    ):

        pending_response = llm_response_by_provider_id.fetchall()

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

        question_answer_list_by_provider_id = database.execute(
            text(QUERY_QUESTION_AND_ANSWER_BY_PROVIDER_ID),
            {"provider_id": provider_id},
        )

        results_map_list = [
            {"Id": row[0], "Question": row[2], "Answer": row[3]}
            for row in question_answer_list_by_provider_id
        ]

        if len(results_map_list) == 0:
            database.close()

            return jsonify(results=[])

        database.execute(
            text(UPDATE_INITIAL_LLM_RESPONSE_STATUS_BY_PROVIDER_ID),
            {"provider_id": provider_id, "status": "processing"},
        )

        database.commit()

        llm_process_thread = threading.Thread(
            target=process_llm_results,
            args=(results_map_list, provider_id),
            daemon=True,
        )

        llm_process_thread.start()

        updated_llm_response_by_provider_id = database.execute(
            text(QUERY_LLM_RESPONSE_BY_PROVIDER_ID),
            {"provider_id": provider_id},
        )

        updated_results_map_list = [
            {"providerId": row[1], "status": row[2], "score": row[3]}
            for row in updated_llm_response_by_provider_id
        ]

        database.close()

        return jsonify(results=updated_results_map_list)
    else:
        results_map_list = [
            {"providerId": row[1], "status": row[2], "score": row[3]}
            for row in llm_response_by_provider_id
        ]

        database.close()

        return jsonify(results=results_map_list)


def process_llm_results(results_map: list[dict[str, Any]], provider_id: int):
    database = get_database()

    llm_response = evaluate_results(results_map)
    score_list = llm_response["scores"]

    total_score = 0
    for llm_response_data in score_list:
        total_score += llm_response_data["score"]

    database.execute(
        text(UPDATE_LLM_RESPONSE_STATUS_SUCCESS_BY_PROVIDER_ID),
        {"score": total_score, "provider_id": provider_id},
    )

    database.commit()
    database.close()
