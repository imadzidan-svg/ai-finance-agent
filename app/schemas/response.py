from pydantic import BaseModel

from app.schemas.ai_insights import AIInsights


class SummaryResponse(BaseModel):

    status: str

    total_income: float

    total_expense: float

    balance: float

    ai_insights: AIInsights