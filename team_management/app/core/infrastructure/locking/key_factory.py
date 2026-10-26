import hashlib
import uuid


class KeyFactory:

    def create_lock_key_from_uuid(self, value: uuid.UUID) -> int:
        digest = hashlib.sha256(value.bytes).digest()
        return int.from_bytes(digest[:8], byteorder="big", signed=True)

    def create_lock_keys_from_list_uuid(
            self, 
            array: list[uuid.UUID]
            ) -> list[int]:
        res = []
        for id in array:
            digest = hashlib.sha256(id.bytes).digest()
            key = int.from_bytes(digest[:8], byteorder="big", signed=True)
            res.append(key)
        return res
