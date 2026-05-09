from pydantic import BaseModel

from typing import List


class AIInsights(BaseModel):

    risk_level: str

    top_category: str

    summary: str

    recommendations: List[str]