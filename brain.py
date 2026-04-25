import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import database

load_dotenv()

class VerificationSchema(BaseModel):
    status: str
    detail: str

class DataSchema(BaseModel):
    response_text: str
    sentiment_score: str
    urgency_level: int
    verification: VerificationSchema
    suggested_action: str
    ticket_id: Optional[int]

class UnifiedResponseSchema(BaseModel):
    type: str
    is_ambiguous: bool
    data: DataSchema

class FeedbackAnalysisSchema(BaseModel):
    sentiment: str
    suggested_action: str

class SentimentFlowEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
        self.model_name = "gemini-3-flash-preview"
        self.client = genai.Client(api_key=self.api_key)
        
    def process(self, message: str, customer_id: str = None, order_id: str = None):
        """
        Analyzes the message and returns the Unified Response Schema.
        """
        if len(message) > 8000:
            message = message[:4000] + "\n...[Content Truncated]...\n" + message[-4000:]
            
        system_prompt = """
        You are SentimentFlow AI. Analyze the customer message.
        Determine if it's an 'enquiry' (e.g. asking a question) or a 'complaint' (frustration, service failure).
        
        Logic Rules:
        If type == 'enquiry', suggested_action MUST be 'AUTO_RESOLVE'. ticket_id MUST be null. urgency_level can be 1. sentiment_score should be Neutral.
        If type == 'complaint', assign a sentiment_score (e.g. Frustrated, Angry), urgency_level (1-10), and a suggested_action (e.g. 'ESCALATE', 'REFUND_OFFER'). ticket_id will be assigned later (keep as null here).
        If the input is too vague, set is_ambiguous: true and ask for more info in response_text.
        """
        
        # Enforce Order ID for complaints immediately before processing
        # We can't know it's a complaint yet unless we just check if it's an enquiry
        # Actually, let the AI classify it. If it returns 'complaint' and we have no order_id, we override it.
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Customer Message: {message}",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=UnifiedResponseSchema,
                    temperature=0.7,
                )
            )
            
            result_content = response.text
            parsed_result = json.loads(result_content)
            
            # Extract data
            data = parsed_result.get("data", {})
            msg_type = parsed_result.get("type", "complaint")
            
            # Strict Policy Override: If it's a complaint but order_id is missing, reject it.
            if msg_type == "complaint" and not order_id:
                return {
                    "type": "complaint",
                    "is_ambiguous": True,
                    "data": {
                        "response_text": "To properly investigate your complaint, I need your Order ID (e.g., ORD-101). Please provide it so I can escalate your issue.",
                        "sentiment_score": "Unknown",
                        "urgency_level": 5,
                        "verification": {"status": "missing", "detail": "Order ID is strictly required for complaints."},
                        "suggested_action": "ESCALATE",
                        "ticket_id": None
                    }
                }
            
            # Verification logic if order_id is provided
            verification_payload = {"status": "missing", "detail": "No order ID provided."}
            
            if order_id:
                tx = database.check_transaction(order_id)
                if tx:
                    if customer_id and tx["customer_id"] != customer_id:
                        verification_payload = {"status": "failed", "detail": "Order ID belongs to a different customer."}
                    else:
                        verification_payload = {"status": "verified", "detail": f"Order verified: {tx['product_name']}"}
                else:
                    verification_payload = {"status": "failed", "detail": f"Order ID {order_id} not found."}
                    
            if "data" not in parsed_result:
                parsed_result["data"] = {}
                
            parsed_result["data"]["verification"] = verification_payload
            
            # DB ticket creation logic inside the engine for complaints
            if msg_type == "complaint" and not parsed_result.get("is_ambiguous", False):
                ticket_id = database.create_ticket(
                    customer_id=customer_id,
                    order_id=order_id if verification_payload["status"] == "verified" else None,
                    message=message,
                    sentiment=data.get("sentiment_score", "Unknown"),
                    urgency_level=data.get("urgency_level", 5),
                    suggested_action=data.get("suggested_action", "ESCALATE")
                )
                parsed_result["data"]["ticket_id"] = ticket_id
                
            return parsed_result
            
        except Exception as e:
            print(f"API Error: {e}")
            # Fallback
            return {
              "type": "complaint",
              "is_ambiguous": True,
              "data": {
                "response_text": "I'm sorry, I'm having trouble processing your request right now. Please try again or wait for a human agent.",
                "sentiment_score": "Unknown",
                "urgency_level": 5,
                "verification": {"status": "missing", "detail": "System error."},
                "suggested_action": "ESCALATE",
                "ticket_id": None
              }
            }

    def analyze_feedback_sentiment(self, message: str) -> dict:
        """
        Takes raw feedback and scores it purely as Positive, Neutral, or Negative,
        along with a suggested action for the business owner.
        """
        import time
        for attempt in range(3):
            try:
                prompt = f"Analyze the following customer feedback: '{message}'. Return the sentiment (Positive, Neutral, Negative) and a suggested action for the business owner to improve. If no action is needed, return an empty string."
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=FeedbackAnalysisSchema,
                        temperature=0.1,
                    )
                )
                parsed = json.loads(response.text)
                sentiment = parsed.get("sentiment", "Neutral").strip().capitalize()
                if sentiment not in ["Positive", "Neutral", "Negative"]:
                    sentiment = "Neutral"
                return {
                    "sentiment": sentiment,
                    "suggested_action": parsed.get("suggested_action", "")
                }
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < 2:
                    print(f"Rate limit hit. Retrying in 10s... (Attempt {attempt+1}/3)")
                    time.sleep(10)
                    continue
                print(f"Feedback Analysis Error: {e}")
                return {"sentiment": "Neutral", "suggested_action": ""}
        return {"sentiment": "Neutral", "suggested_action": ""}
