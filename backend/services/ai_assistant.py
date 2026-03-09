"""
AI Tax Assistant — answers questions about the user's tax situation
using their extracted document data as context.
"""
from openai import OpenAI
import os, json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are TaxAI, an expert US tax assistant. You help users understand
their tax documents, identify deductions, and answer tax questions clearly.
Always be accurate, explain things simply, and remind users you're an AI —
they should consult a licensed CPA for official advice.
Keep responses concise and actionable."""

def chat_with_ai(user_message: str, tax_context: dict = None) -> str:
    """
    Send a message to the AI assistant with optional tax context injected.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if tax_context:
        context_str = json.dumps(tax_context, indent=2)
        messages.append({
            "role": "system",
            "content": f"The user's current tax data:\n```json\n{context_str}\n```"
        })

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=600,
        temperature=0.3,
    )
    return response.choices[0].message.content

def generate_tax_summary(tax_data: dict) -> str:
    """
    Auto-generate a plain-English summary of the user's tax situation.
    """
    prompt = f"""Based on this tax data, write a clear 3-paragraph summary:
1. Income overview
2. Deductions and what's being used
3. Whether they owe money or get a refund and why

Tax data: {json.dumps(tax_data)}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.4,
    )
    return response.choices[0].message.content
