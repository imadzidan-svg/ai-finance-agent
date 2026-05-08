from openai import OpenAI
from app.utils.decorators import simple_cache,retry

from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

@retry(max_attempts=3)
@simple_cache
def generate_ai_insights(summary):

    try:

        prompt = f"""
        You are a financial analytics assistant.
    
        Analyze the following financial summary.
    
        Provide:
        1. Spending observations
        2. Potential concerns
        3. Positive financial indicators
    
        Keep response concise and business-friendly.
    
        Data:
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

        return response.choices[0].message.content
    except Exception as e:
        return f"AI insight generation failed: {str(e)}"