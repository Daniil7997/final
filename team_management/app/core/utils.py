import uuid


def generate_invite_code() -> str:
    return str(uuid.uuid7())
