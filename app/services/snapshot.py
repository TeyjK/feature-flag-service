from typing import Optional
snapshot: dict[str, dict] = {}

def get_from_snapshot(flag_id: str) -> Optional[dict]:
    return snapshot.get(flag_id)

def update_snapshot(flag_id: str, flag_data: dict) -> None:
    snapshot[flag_id] = dict(flag_data)

def delete_from_snapshot(flag_id: str) -> None:
    snapshot.pop(flag_id, None)