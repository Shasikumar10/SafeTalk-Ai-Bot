from detoxify import Detoxify

model = Detoxify("unbiased")

THRESHOLD = 0.8

def safety_check(text: str):
    scores = model.predict(text)
    for k, v in scores.items():
        if v >= THRESHOLD:
            return {
                "response_type": "safety_block",
                "category": k,
                "score": round(float(v), 3),
                "message": "I can’t help with harmful or abusive content."
            }
    return None
