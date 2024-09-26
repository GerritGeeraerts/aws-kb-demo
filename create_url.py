import urllib.parse

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64

def encrypt_with_public_key(message):
    with open('public_key.pem', 'rb') as key_file:
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

kb_id = input("I will generate an access url, give me the aws-kb-id: ")
print(f"http://localhost:8501?kb-id={encrypt_with_public_key(kb_id)}")