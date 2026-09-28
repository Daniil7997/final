import uuid
import hashlib


class KeyFactory:
    def uuid_to_bigint(self, value: uuid.UUID) -> int:
        digest = hashlib.sha256(value.bytes).digest()
        return int.from_bytes(digest[:8], byteorder="big", signed=True)
