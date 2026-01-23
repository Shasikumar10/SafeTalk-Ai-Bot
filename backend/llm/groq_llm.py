import os
from groq import Groq
from dotenv import load_dotenv

# Load env first
load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing")

client = Groq(api_key=GROQ_API_KEY)

# ✅ GUARANTEED WORKING MODEL
MODEL = "llama-3.1-8b-instant"


def answer_general(question: str) -> str:
    res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
        temperature=0.4,
    )
    return res.choices[0].message.content.strip()


def answer_with_context(context, question: str) -> str:
    prompt = f"""
Answer using ONLY the context below.
If not found, say "I don't know".

Context:
{chr(10).join(context)}

Question:
{question}
"""
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return res.choices[0].message.content.strip()
