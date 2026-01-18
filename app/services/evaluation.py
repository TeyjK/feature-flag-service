import mmh3

def evaluate_flag_for_user(user_id: str, flag_id: str, rollout_percentage: int) -> bool:
    hash_value = mmh3.hash(f"{user_id}:{flag_id}", signed = False)
    bucket = hash_value % 10000
    return bucket < (rollout_percentage*100)