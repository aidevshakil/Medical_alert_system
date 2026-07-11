from typing import Dict, Any
import json
from openai import AsyncOpenAI
from app.core import config

client = AsyncOpenAI(api_key=config.settings.API_KEY)

SYSTEM_PROMPT = (
    "You are a highly experienced clinical triage assistant. "
    "Your task is to read a patient's short transcript or voice note and determine the urgency of their condition. "
    "Classify urgency as one of: HIGH, MEDIUM, or LOW. "
    "Also identify relevant symptom tags (like 'chest_pain', 'shortness_of_breath', 'fever', 'fall', etc.) and provide a concise reason for your assessment. "
    "Respond strictly as a single JSON object with keys: 'urgency', 'tags' (array), and 'reason'. "
    "Do not provide any text outside the JSON object."
)

async def profile_text(transcribed_text: str) -> Dict[str, Any]:
    """
    Send the transcript to GPT-4-mini for dynamic urgency classification.
    Returns a dict with:
        { "urgency": "HIGH|MEDIUM|LOW", "tags": [...], "reason": "short explanation" }
    """
    user_prompt = (
        f"Patient transcript:\n\"\"\"\n{transcribed_text}\n\"\"\"\n\n"
        "Analyze the patient's condition and return only a single JSON object "
        "with 'urgency', 'tags', and 'reason'."
    )

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=250
    )

    content = resp.choices[0].message.content.strip()

    try:
        result = json.loads(content)
    except Exception:
        # Fallback if GPT responds incorrectly
        result = {
            "urgency": "MEDIUM",
            "tags": [],
            "reason": content  # return raw content for debugging
        }

    return result



# from typing import Dict, Any
# import json
# from openai import AsyncOpenAI
# from app.core import config

# client = AsyncOpenAI(api_key=config.settings.API_KEY)

# SYSTEM_PROMPT = (
#     "You are a clinical triage assistant. Given a short patient utterance or transcript, "
#     "classify the urgency into one of: HIGH, MEDIUM, LOW. Provide a short reason and any tags (e.g., 'chest_pain', 'breathless', 'fall'). "
#     "Respond with a single JSON object only."
# )

# EXAMPLES = [
#     {
#         "input": "My chest hurts and I'm short of breath and feeling faint.",
#         "output": {"urgency": "HIGH", "tags": ["chest_pain", "shortness_of_breath"], "reason": "Chest pain + dyspnea = potential cardiac/respiratory emergency"}
#     },
#     {
#         "input": "I have had a mild headache since morning but I can move and speak normally.",
#         "output": {"urgency": "LOW", "tags": ["headache"], "reason": "Mild headache without red flags"}
#     }
# ]

# async def profile_text(text: str) -> Dict[str, Any]:
#     """
#     Sends the transcript text to an LLM and returns structured classification:
#       { "urgency": "HIGH|MEDIUM|LOW", "tags": [...], "reason": "..." }
#     """
#     examples_prompt = "\n\n".join(
#         f"Input: {ex['input']}\nOutput: {json.dumps(ex['output'])}" for ex in EXAMPLES
#     )
#     user_message = (
#         f"{examples_prompt}\n\nNow classify this transcript:\n\n\"\"\"\n{text}\n\"\"\"\n\n"
#         "Return only a single JSON object with keys: urgency, tags (array), reason (short)."
#     )

#     resp = await client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_message},
#         ],
#         max_tokens=200,
#         temperature=0.0,
#     )

#     content = resp.choices[0].message.content.strip()
#     # Try to parse JSON; fall back to a best-effort parse
#     try:
#         result = json.loads(content)
#     except Exception:
#         # minimal fallback: return unstructured text as reason
#         result = {"urgency": "MEDIUM", "tags": [], "reason": content}
#     return result

def analyze_text(transcribed_text: str) -> dict:
    urgency_keywords = ["urgent", "emergency", "critical", "immediate", "asap"]
    urgency_score = 0

    for keyword in urgency_keywords:
        if keyword in transcribed_text.lower():
            urgency_score += 1

    urgency_level = "low"
    if urgency_score > 2:
        urgency_level = "high"
    elif urgency_score > 0:
        urgency_level = "medium"

    return {
        "transcribed_text": transcribed_text,
        "urgency_level": urgency_level,
        "urgency_score": urgency_score
    }