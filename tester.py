#
# {
#                                 "andAll": [
#                                     {
#                                         "equals":
#                                             {
#                                                 "key": "x-amz-bedrock-kb-data-source-id",
#                                                 "value": "EI4WVPC5GR"
#                                             }
#                                     },
#                                     {
#                                         "equals":
#                                             {
#                                                 "key": "x-amz-bedrock-kb-data-source-id",
#                                                 "value": "EI4WVPC5GR"
#                                             }
#                                     },
#                                 ]
#                             }

#
import os

import boto3
from boto3.session import Session
from dotenv import load_dotenv

load_dotenv()

# Initialize a session using boto3
sts_client = boto3.client('sts')


# Assume the role
response = sts_client.assume_role(
    RoleArn='arn:aws:iam::730335415390:role/allow-acces-to-sumsum-s3-bucket-role',  # Replace with your Role ARN
    RoleSessionName='S3AccessSession'
)

# Extract temporary credentials
credentials = response['Credentials']

# Use the temporary credentials to create a session
session = Session(
    aws_access_key_id=credentials.get('AccessKeyId'),
    aws_secret_access_key=credentials.get('SecretAccessKey'),
    aws_session_token=credentials.get('SessionToken')
)

# Initialize S3 client using the assumed role session
s3_client = session.client('s3')

# List the contents of the bucket
bucket_name = 'rag-demo-sumsum-files'

try:
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        print(obj['Key'])
except Exception as e:
    print(f'Error: {e}')