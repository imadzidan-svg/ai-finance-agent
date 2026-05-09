from fastapi import FastAPI, UploadFile, File
import pandas as pd
from app.database import engine
from app.models.upload import Upload
from app.models.transaction import Transaction
from app.database import Base,get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.services.transaction_service import summarize_transactions
from app.utils.security import verify_api_key
from app.schemas.response import SummaryResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "AI Finance Agent Running"}

@app.get("/uploads")
def get_uploads(db: Session = Depends(get_db)):

    uploads = db.query(Upload).all()

    return uploads

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):

    transactions = db.query(Transaction).all()

    total_income = sum(t.amount for t in transactions if t.type == "income")

    total_expense = sum(t.amount for t in transactions if t.type == "expense")

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "transaction_count": len(transactions)
    }


@app.post("/automation/analyze",response_model=SummaryResponse)
async def automation_analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):

    df = pd.read_csv(file.file)

    summary = summarize_transactions(df)

    upload_record = Upload(

        filename=file.filename,

        total_income=summary["total_income"],

        total_expense=summary["total_expense"],

        balance=summary["balance"],

        ai_insights=summary["ai_insights"]
    )

    db.add(upload_record)

    db.commit()

    db.refresh(upload_record)

    for _, row in summary["dataframe"].iterrows():
        transaction = Transaction(

            description=row["description"],

            amount=row["amount"],

            type=row["type"],

            category=row["category"]
        )

        db.add(transaction)

    db.commit()

    db.refresh(transaction)

    del summary["dataframe"]

    return {
        "status": "success",
        "total_income": summary["total_income"],
        "total_expense": summary["total_expense"],
        "balance": summary["balance"],
        "ai_insights": summary["ai_insights"]
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), db: Session = Depends(get_db)):

    df = pd.read_csv(file.file)

    summary = summarize_transactions(df)

    upload_record = Upload(

        filename=file.filename,

        total_income=summary["total_income"],

        total_expense=summary["total_expense"],

        balance=summary["balance"],

        ai_insights=summary["ai_insights"]
    )

    db.add(upload_record)

    db.commit()

    db.refresh(upload_record)

    for _, row in summary["dataframe"].iterrows():
        transaction = Transaction(

            description=row["description"],

            amount=row["amount"],

            type=row["type"],

            category=row["category"]
        )

        db.add(transaction)

    db.commit()

    db.refresh(transaction)

    del summary["dataframe"]

    return summary