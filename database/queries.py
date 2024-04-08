QUERY_SERVICE_PROVIDER_BY_ID="SELECT * FROM `freelance_service_provider` WHERE provider_id = :provider_id;"
QUERY_LLM_RESPONSE_BY_PROVIDER_ID="SELECT * FROM `llm_response` WHERE provider_id = :provider_id;"
UPDATE_INITIAL_LLM_RESPONSE_STATUS_BY_PROVIDER_ID="INSERT INTO `llm_response` (`provider_id`, `status`, `score`) VALUES (:provider_id, :status, NULL);"
QUERY_QUESTION_AND_ANSWER_BY_PROVIDER_ID="""
    SELECT questions.question_id, questions.category, questions.question, responses.answer
    FROM questions
    INNER JOIN responses ON questions.question_id=responses.question_id
    WHERE provider_id=:provider_id;
"""
UPDATE_LLM_RESPONSE_STATUS_SUCCESS_BY_PROVIDER_ID="""
    UPDATE `llm_response`
    SET `status` = 'success', `score` = :score
    WHERE `llm_response`.`provider_id` = :provider_id
"""