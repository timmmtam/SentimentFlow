from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from brain import SentimentFlowEngine
import database

# Initialize the FastAPI application with metadata
app = FastAPI(
    title="SentimentFlow API",
    description="Backend API for SentimentFlow utilizing Google Gemini",
    version="1.1"
)

# Initialize the reasoning engine (Gemini)
engine = SentimentFlowEngine()

# Data models for request validation
class ProcessRequest(BaseModel):
    message: str
    customer_id: Optional[str] = "CUST-001"
    order_id: Optional[str] = None

class TicketUpdateRequest(BaseModel):
    status: str

class FeedbackRequest(BaseModel):
    message: str
    customer_id: Optional[str] = "CUST-001"

class FeedbackUpdateRequest(BaseModel):
    suggested_action: str

class TodoRequest(BaseModel):
    task: str

class TodoUpdateRequest(BaseModel):
    status: str

@app.get("/")
def health_check():
    """
    Health check endpoint to verify that the FastAPI backend is running.
    Used by the Streamlit frontend for the 'System Status' indicator.
    """
    return {"status": "Online"}

@app.post("/process")
async def process_message(request: ProcessRequest):
    """
    Main endpoint for processing customer messages.
    Accepts a user message, calls the SentimentFlowEngine for classification,
    and handles routing (either providing an FAQ response or creating a Ticket).
    Returns the Unified Response Schema.
    """
    result = engine.process(request.message, request.customer_id, request.order_id)
    return result

@app.get("/tickets")
def get_tickets():
    """
    Retrieves all tickets from the SQLite database.
    Used by the Merchant Dashboard to populate the active complaints queue.
    """
    return database.get_tickets()

@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, update: TicketUpdateRequest):
    """
    Updates the status of a specific ticket (e.g., changing from 'New' to 'Resolved').
    Triggered when an admin clicks 'Approve & Resolve' in the dashboard.
    """
    database.update_ticket_status(ticket_id, update.status)
    return {"success": True, "ticket_id": ticket_id, "new_status": update.status}

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """
    Accepts feedback from the dedicated frontend web form, scores it with AI,
    and saves it to the database.
    """
    result = engine.analyze_feedback_sentiment(request.message)
    sentiment_score = result.get("sentiment", "Neutral")
    suggested_action = result.get("suggested_action", "")
    database.create_feedback(request.customer_id, request.message, sentiment_score, suggested_action)
    return {"success": True, "sentiment_score": sentiment_score, "suggested_action": suggested_action}

@app.get("/feedback")
def get_feedback():
    """
    Retrieves all Feedback from the SQLite database.
    Used by the Merchant Dashboard to populate the Sentiment Analysis tab.
    """
    return database.get_all_feedback()

@app.patch("/feedback/{feedback_id}")
def update_feedback(feedback_id: int, update: FeedbackUpdateRequest):
    database.update_feedback_action(feedback_id, update.suggested_action)
    return {"success": True}

@app.get("/faqs")
def get_faqs():
    """
    Retrieves all Knowledge Base FAQs for the Documentation sub-page.
    """
    return database.get_all_faqs()

@app.post("/todos")
def create_todo(request: TodoRequest):
    database.create_todo(request.task)
    return {"success": True}

@app.get("/todos")
def get_todos():
    return database.get_todos()

@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, update: TodoUpdateRequest):
    database.update_todo_status(todo_id, update.status)
    return {"success": True, "todo_id": todo_id, "new_status": update.status}
