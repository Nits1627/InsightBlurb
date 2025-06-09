import hashlib

def sha256_of_dict(data: dict) -> str:
    import json
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()