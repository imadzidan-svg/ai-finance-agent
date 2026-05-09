from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends, Form
import pandas as pd
from app.database import engine, SessionLocal
from app.models.upload import Upload
from app.models.transaction import Transaction
from app.database import Base,get_db
from sqlalchemy.orm import Session
from app.services.transaction_service import summarize_transactions
from app.utils.security import verify_api_key
from app.schemas.response import SummaryResponse
import shutil
import requests
from app.config import MAKE_WEBHOOK_URL

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "AI Finance Agent Running"}

@app.get("/uploads")
def get_uploads(db: Session = Depends(get_db)):

    uploads = db.query(Upload).all()

    return uploads

@app.get("/uploads/{upload_id}")
def get_upload_status(
    upload_id: int,
    db: Session = Depends(get_db)
):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    transactions = db.query(Transaction).filter(
        Transaction.upload_id == upload_id
    ).all()

    return {
        "id": upload.id,
        "filename": upload.filename,
        "status": upload.processing_status,
        "is_processed": upload.is_processed,
        "total_income": upload.total_income,
        "total_expense": upload.total_expense,
        "balance": upload.balance,
        "ai_insights": upload.ai_insights,
        "transactions": [
            {
                "description": t.description,
                "amount": t.amount,
                "type": t.type,
                "category": t.category
            }
            for t in transactions
        ]
    }

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

def process_file_background(
    file_path: str,
    upload_id: int
):

    db = SessionLocal()

    try:

        df = pd.read_csv(file_path)

        summary = summarize_transactions(df)

        upload = db.query(Upload).filter(
            Upload.id == upload_id
        ).first()

        upload.total_income = summary["total_income"]

        upload.total_expense = summary["total_expense"]

        upload.balance = summary["balance"]

        upload.ai_insights = summary["ai_insights"]

        for _, row in summary["dataframe"].iterrows():
            transaction = Transaction(

                upload_id=upload_id,

                description=row["description"],

                amount=row["amount"],

                type=row["type"],

                category=row["category"]
            )

            db.add(transaction)

        upload.is_processed = True

        upload.processing_status = "completed"

        db.commit()

        # Call make webhook passing the requested data in order to send an email to the sender
        # with ai insights
        requests.post(

            MAKE_WEBHOOK_URL,

            json={

                "upload_id": upload.id,

                "sender_email": upload.sender_email,

                "sender_name": upload.sender_name,

                "email_subject": upload.email_subject,

                "status": upload.processing_status,

                "total_income": upload.total_income,

                "total_expense": upload.total_expense,

                "balance": upload.balance,

                "ai_insights": upload.ai_insights
            }
        )

    except Exception as e:

        upload = db.query(Upload).filter(
            Upload.id == upload_id
        ).first()

        upload.processing_status = "failed"

        db.commit()

    finally:

        db.close()

@app.post("/automation/analyze")
async def automation_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    sender_email: str = Form(...),
    sender_name: str = Form(...),
    email_subject: str = Form(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    upload_record = Upload(

        filename=file.filename,

        sender_email=sender_email,

        sender_name=sender_name,

        email_subject=email_subject,

        total_income=0,

        total_expense=0,

        balance=0,

        ai_insights={},

        is_processed=False,

        processing_status="processing"
    )

    db.add(upload_record)

    db.commit()

    db.refresh(upload_record)

    background_tasks.add_task(

        process_file_background,

        temp_path,

        upload_record.id
    )

    return {
        "status": "processing",
        "upload_id": upload_record.id
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