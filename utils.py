import re
from pprint import pprint
from typing import List
import boto3
import urllib.parse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64

from config import Config


def s3_path_to_relative_path(s3_path: str) -> str:
    """use this regex replace:  to replace the s3 path with an empty string"""
    return re.sub(r's3://[^/]*/', "", s3_path)


def backend_to_friendly(name: str) -> str:
    """Convert backend name to friendly name"""
    if not name:
        return ""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).replace('_', ' ').replace('-', ' ').title().replace(' ', '')



def encrypt_with_public_key(message):
    with open(Config.PUBLIC_KEY_PATH, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    message_bytes = message.encode('utf-8')
    encrypted = public_key.encrypt(
        message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted = base64.b64encode(encrypted).decode('utf-8')
    return urllib.parse.quote(encrypted)

def decrypt_with_private_key(encrypted_message):
    with open(Config.PRIVATE_KEY_PATH, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    try:
        encrypted_message = urllib.parse.unquote(encrypted_message)
        encrypted_bytes = base64.b64decode(encrypted_message)
        decrypted_message = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message.decode('utf-8')
    except Exception as e:
        print("Decryption failed:", e)
        return None

class Chat:
    def __init__(self, kb_id: str):
        self.client = boto3.client('bedrock-agent-runtime', region_name=Config.LOCATION)
        self.client_bedrock_agent = boto3.client('bedrock-agent', region_name=Config.LOCATION)
        self.kb_id = kb_id
        data_source_ids = self.get_data_source_ids()
        self.filter = self.get_kb_datasource_filter(data_source_ids)
        self.kb_name = self.__get_kb_name(kb_id)

    def __get_kb_name(self, knowledge_base_id: str) -> str:
        # Call the get_knowledge_base API with the provided knowledge base ID
        response = self.client_bedrock_agent.get_knowledge_base(
            knowledgeBaseId=knowledge_base_id
        )
        # Retrieve the name of the knowledge base
        knowledge_base_name = response['knowledgeBase']['name']
        return knowledge_base_name


    def get_data_source_ids(self) -> List[str]:
        response = self.client_bedrock_agent.list_data_sources(
            knowledgeBaseId=self.kb_id,
            maxResults=100,
        )
        results = [data_source.get('dataSourceId') for data_source in response.get('dataSourceSummaries', [])]
        print(f"KB: {self.kb_id} has data sources: {results}")
        return results

    def get_kb_datasource_filter(self, data_source_ids: List[str]) -> dict:
        if len (data_source_ids) == 0:
            return {}
        if len(data_source_ids) == 1:
            return {
                'equals': {
                    'key': 'x-amz-bedrock-kb-data-source-id',
                    'value': data_source_ids[0]
                }
            }
        filter = {"orAll": []}
        for data_source_id in data_source_ids:
            filter['orAll'].append({
                "equals": {
                    "key": "x-amz-bedrock-kb-data-source-id",
                    "value": data_source_id
                }
            })
        return filter

    def inference(self, text: str, ):
        if not self.kb_id:
            raise ValueError("Knowledge Base ID is required")
        print(f'inferencing: {text}')
        pprint(self.filter)
        # https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html
        response = self.client.retrieve_and_generate(
            input={
                'text': text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': self.kb_id,
                    'modelArn': Config.MODEL_ARN,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'overrideSearchType': Config.SEARCH_TYPE,
                            "numberOfResults": Config.NUMBER_OF_RETRIEVED_DOCUMENTS,
                            "filter": self.filter
                        }
                    },
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "maxTokens": Config.MAX_OUTPUT_TOKENS,
                                "stopSequences": [
                                    "\nObservation"
                                ],
                                "temperature": Config.TEMPERATURE,
                                "topP": Config.TOP_P,
                            }
                        },
                        "promptTemplate": {
                            "textPromptTemplate": Config.PROMPT_TEMPLATE
                        }
                    },
                }
            }
        )

        output = response.get('output', {}).get('text', '')
        clean_citations = []
        raw_citations = response['citations'][0]['retrievedReferences']

        for citation in raw_citations:
            text = citation.get('content', {}).get('text', '')
            if citation.get('location', {}).get('type', '') == 'WEB':
                url = citation.get('location', {}).get('webLocation', {}).get('url', '')
                url = re.sub(r'(https://|http://)', "", url)
                clean_citations.append({
                    "citation": text,
                    "url": url
                })
                continue
            if citation.get('location', {}).get('type', '') == 'S3':
                url = citation.get('location', {}).get('s3Location', {}).get('uri', '')
                url = s3_path_to_relative_path(url)
                clean_citations.append({
                    "citation": text,
                    "url": url
                })
        return {
            "output": output,
            "citations": clean_citations
        }


if __name__ == "__main__":
    chat_client = Chat(kb_id="2QSIT8PNME")
    print(chat_client.get_kb_name("2QSIT8PNME"))