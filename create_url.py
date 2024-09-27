from utils import encrypt_with_public_key, decrypt_with_private_key

if __name__ == "__main__":
    kb_id = input("I will generate an access url, give me the aws-kb-id: ")
    encrypted = encrypt_with_public_key(kb_id)
    decrypted = decrypt_with_private_key(encrypted)
    print(f"Url for KB[{decrypted}]: http://localhost:8501?kb-id={encrypted}")