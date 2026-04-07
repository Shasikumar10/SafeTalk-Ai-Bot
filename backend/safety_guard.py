_model = None

HARMFUL_KEYWORDS = [
    "bomb", "weapon", "kill", "suicide", "murder", "illegal", "drug", "hack",
    "stolen", "attacker", "terrorist", "abuse", "rape", "hate"
]

def get_safety_model():
    global _model
    if _model is None:
        print("Loading Safety Monitor (Detoxify)...")
        from detoxify import Detoxify
        _model = Detoxify("unbiased")
    return _model

def safety_check(text: str):
    norm_text = text.lower()
    
    # 1. Faster Keyword Check (0 bytes RAM)
    for kw in HARMFUL_KEYWORDS:
        if kw in norm_text:
            return {
                "response_type": "safety_block",
                "category": "keyword_filter",
                "message": f"Found sensitive term: {kw}. I can't assist with that request."
            }

    # 2. Delayed AI Check (Loads into RAM only if needed)
    try:
        model = get_safety_model()
        scores = model.predict(text)
        THRESHOLD = 0.8
        for k, v in scores.items():
            if v >= THRESHOLD:
                return {
                    "response_type": "safety_block",
                    "category": k,
                    "score": round(float(v), 3),
                    "message": "I can’t help with harmful or abusive content."
                }
    except Exception as e:
        print(f"Safety model warning (Likely RAM limit): {e}")
        
    return None
