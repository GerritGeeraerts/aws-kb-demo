import re
from pprint import pprint
from typing import List

import boto3
from boto3 import Session
from dotenv import load_dotenv
import urllib.parse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64
from config import Config


def s3_path_to_relative_path(s3_path: str) -> str:
    """use this regex replace:  to replace the s3 path with an empty string"""
    return re.sub(r's3://[^/]*/', "", s3_path)


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
        # load_dotenv()
        # self.session = self.__get_sessoin()
        self.client = boto3.client('bedrock-agent-runtime', region_name=Config.LOCATION)
        self.kb_id = kb_id
        data_source_ids = self.get_data_source_ids()
        self.filter = self.get_kb_datasource_filter(data_source_ids)

    # def __get_sessoin(self):
    #     sts_client = boto3.client('sts')
    #
    #     # Assume the role
    #     response = sts_client.assume_role(
    #         RoleArn='arn:aws:iam::730335415390:role/my-st-app-role',  # Replace with your Role ARN
    #         RoleSessionName='S3AccessSession'
    #     )
    #
    #     credentials = response['Credentials']
    #
    #     # Use the temporary credentials to create a session
    #     session = Session(
    #         aws_access_key_id=credentials.get('AccessKeyId'),
    #         aws_secret_access_key=credentials.get('SecretAccessKey'),
    #         aws_session_token=credentials.get('SessionToken'),
    #         profile_name="AWSAdministratorAccess-730335415390",
    #     )
    #     return session

    def get_data_source_ids(self) -> List[str]:
        client = boto3.client('bedrock-agent', region_name=Config.LOCATION)
        response = client.list_data_sources(
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
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'overrideSearchType': 'HYBRID',
                            "numberOfResults": 10,
                            "filter": self.filter
                        }
                    }
                }
            }
            #     # "externalSourcesConfiguration": {
            #     #     "generationConfiguration": {
            #     #         "promptTemplate": {
            #     #             "textPromptTemplate": "prompt template"
            #     #         }
            #     #     }
            #     # },
            #
            # }
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