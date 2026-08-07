from app.core.auth import create_access_token, verify_access_token

token = create_access_token(
    {
        "sub": "test@example.com"
    }
)

print("Generated Token:")
print(token)

print("\nDecoded Payload:")
print(verify_access_token(token))