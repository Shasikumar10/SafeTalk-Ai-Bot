import os
from groq import Groq
from dotenv import load_dotenv

# Load env first
load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing")

client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"


chat_history = []

def answer_general(prompt: str) -> str:
    global chat_history
    messages = list(chat_history)
    messages.append({"role": "user", "content": prompt})
    
    res = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.4
    )
    answer = res.choices[0].message.content.strip()
    
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": answer})
    if len(chat_history) > 10: chat_history = chat_history[-10:]
    
    return answer


def answer_with_context(context, question: str, instruction: str = "") -> str:
    prompt = f"""
{instruction}
Answer using ONLY the context below.
If not found, say "I don't know".

Context:
{chr(10).join(context)}

Question:
{question}
"""
    global chat_history
    messages = list(chat_history)
    messages.append({"role": "user", "content": prompt})
    
    res = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
    )
    answer = res.choices[0].message.content.strip()
    
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})
    if len(chat_history) > 10: chat_history = chat_history[-10:]
    
    return answer





