"""
3.9 Safety Guard — Detoxify (Hugging Face)
-----------------------------------------
Detects abusive/offensive/toxic content using a pretrained model.
Deterministic thresholds, offline, auditable.
"""

from detoxify import Detoxify

# Load model once at startup
# Options: 'original', 'unbiased', 'multilingual'
MODEL_NAME = "unbiased"
model = Detoxify(MODEL_NAME)

# Thresholds (tune for hackathon clarity)
THRESHOLDS = {
    "toxicity": 0.80,
    "severe_toxicity": 0.70,
    "obscene": 0.70,
    "threat": 0.70,
    "insult": 0.75,
    "identity_attack": 0.70,
}

def safety_check(text: str):
    """
    Returns:
      None -> Safe
      dict -> Blocked with reason and scores
    """
    if not text or not text.strip():
        return None

    scores = model.predict(text)

    # Check against thresholds
    for category, threshold in THRESHOLDS.items():
        score = scores.get(category, 0.0)
        if score >= threshold:
            return {
                "response_type": "safety_block",
                "reason": "toxic_content",
                "category": category,
                "score": round(float(score), 3),
                "message": (
                    "I can’t help with abusive or harmful language. "
                    "Please rephrase your request."
                ),
            }

    return None
