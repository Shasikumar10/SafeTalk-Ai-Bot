import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama3-70b-8192"

def answer_with_context(context, question):
    prompt = f"""
Answer ONLY using the context below.
If the answer is not present, say "I don't know".

Context:
{chr(10).join(context)}

Question:
{question}
"""
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return res.choices[0].message.content.strip()

def answer_general(question):
    prompt = f"""
Answer the question clearly and accurately.
If unsure, say you are not certain.

Question:
{question}
"""
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return res.choices[0].message.content.strip()
