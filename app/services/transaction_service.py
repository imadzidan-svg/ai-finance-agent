import pandas as pd
from app.services.ai_service import generate_ai_insights
from app.utils.logger import logger
from app.utils.decorators import execution_time


def categorize_transaction(description: str):

    description = description.lower()

    if "uber" in description:
        return "transport"

    elif "restaurant" in description:
        return "food"

    elif "salary" in description:
        return "income"

    return "other"

@execution_time
def summarize_transactions(df: pd.DataFrame):

    logger.info("Starting transaction summarization")

    df["category"] = df["description"].apply(categorize_transaction)

    logger.info("Transactions categorized")

    total_income = df[df["type"] == "income"]["amount"].sum()

    total_expense = df[df["type"] == "expense"]["amount"].sum()

    balance = total_income - total_expense

    category_summary = (
        df.groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    insights = generate_insights(
        category_summary,
        total_income,
        total_expense
    )

    ai_insights = generate_ai_insights(category_summary)

    logger.info("Summary generated successfully")

    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "balance": float(balance),
        "transactions": len(df),
        "categories": category_summary,
        "insights": insights,
        "ai_insights": ai_insights,
        "dataframe": df
    }

def generate_insights(category_summary, total_income, total_expense):

    insights = []

    if category_summary.get("food", 0) > 300:
        insights.append("Food spending is high.")

    if category_summary.get("transport", 0) > 150:
        insights.append("Transport spending is high.")

    if total_expense > total_income:
        insights.append("Warning: expenses exceed income.")

    if total_income > total_expense:
        insights.append("Income is greater than expenses.")

    return insights

