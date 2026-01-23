import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama3-70b-8192"


def answer_with_context(context: list[str], question: str):
    prompt = f"""
Answer the question ONLY using the context below.
If the answer is not present, say "I don't know".

Context:
{chr(10).join(context)}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
