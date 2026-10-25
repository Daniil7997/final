import uuid
from datetime import UTC, datetime

import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from pwdlib import PasswordHash

from app.core.config import settings
from app.schemas.auth import AccessTokensPayload, Tokens

private_key_bytes = bytes.fromhex(settings.app.PRIVATE_KEY_HEX)

PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
TOKEN_ALGORITHM = 'EdDSA'
HASH_ALGORITHM = PasswordHash.recommended()  # алгоритм Argon2


def hash_password(password: str) -> str:
    return HASH_ALGORITHM.hash(password)


def verify_password(raw_password: str, hash_password: str) -> bool:
    return HASH_ALGORITHM.verify(raw_password, hash_password)


def create_tokens(user_id: uuid.UUID) -> Tokens:
    now_unix = int(datetime.now(UTC).timestamp())
    exp_access_unix = settings.app.access_tokens_ttl + now_unix

    json_access_payload = AccessTokensPayload(
        sub=user_id,  # ID пользователя
        iat=now_unix,  # Время создания
        exp=exp_access_unix,  # Время действия
        token_type="access"  # Тип токена
    ).model_dump(mode='json')

    access_token = jwt.encode(json_access_payload,
                              PRIVATE_KEY,
                              algorithm=TOKEN_ALGORITHM)
    return Tokens(access=access_token)


def decode_token(token):
    token = jwt.decode(algorithms=TOKEN_ALGORITHM,
                       key=PRIVATE_KEY,
                       jwt=token)

    if token['token_type'].lower() == 'access':
        result = AccessTokensPayload(**token)
    return result
