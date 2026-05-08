from openai import OpenAI
from app.utils.decorators import simple_cache,retry
from app.config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

@retry(max_attempts=3)
@simple_cache
def generate_ai_insights(summary):

    try:

        prompt = f"""
        You are a financial analytics assistant.

        Analyze the following financial data.

        Return ONLY valid JSON.
        
        Required JSON format:

        {{
            "risk_level": "low | medium | high",
            "top_category": "category name",
            "summary": "short summary",
            "recommendations": [
                "recommendation 1",
                "recommendation 2"
            ]
        }}

        Financial data:
        {summary}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        return json.loads(content)

    except Exception as e:
        return f"AI insight generation failed: {str(e)}"