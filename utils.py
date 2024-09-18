import re

import boto3
from dotenv import load_dotenv
import string
import urllib.parse
import random

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
    def __init__(self):
        load_dotenv()
        self.client = boto3.client('bedrock-agent-runtime', region_name="us-east-1")

    def inference(self, kb_id, text, ):
        if not kb_id:
            raise ValueError("Knowledge Base ID is required")
        print(f'inferencing: {text}')
        response = self.client.retrieve_and_generate(
            input={
                'text': text
            },
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'overrideSearchType': 'HYBRID'
                        }
                    }
                },
                'type': 'KNOWLEDGE_BASE'
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