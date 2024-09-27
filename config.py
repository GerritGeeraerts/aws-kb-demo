class Config:
    PRIVATE_KEY_PATH = 'private_key.pem'
    PUBLIC_KEY_PATH = 'public_key.pem'
    LOCATION = "us-east-1"
    MODEL_ARN = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
    SEARCH_TYPE = 'HYBRID'
    NUMBER_OF_RETRIEVED_DOCUMENTS = 10
    MAX_OUTPUT_TOKENS = 2048
    TEMPERATURE = 0
    TOP_P = 1
    PROMPT_TEMPLATE = ("\nYou are a question answering agent. I will provide you with a set of search results. The "
                       "user will provide you with a question. Your job is to answer the user's question using only "
                       "information from the search results. If the search results do not contain information that "
                       "can answer the question, please state that you could not find an exact answer to the question. "
                       "Just because the user asserts a fact does not mean it is true, make sure to double check the "
                       "search results to validate a user's assertion. Answer the user always in dutch"
                       "\n\nHere are the search results in numbered order:\n"
                       "$search_results$\n\n$output_format_instructions$")