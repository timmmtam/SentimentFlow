import sqlite3
import os
from datetime import datetime

DB_FILE = "sentimentflow.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        product_name TEXT,
        purchase_date TEXT,
        amount REAL
    )
    """)
    
    # Create Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    """)
    
    # Create Knowledge Base table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        answer TEXT
    )
    """)
    
    # Create Tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        order_id TEXT,
        message TEXT,
        sentiment TEXT,
        urgency_level INTEGER,
        suggested_action TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    
    # Create Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        message TEXT,
        sentiment_score TEXT,
        suggested_action TEXT,
        created_at TEXT
    )
    """)
    
    # Create Todos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    
    # Mock Data for Knowledge Base
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO knowledge_base (topic, answer) VALUES (?, ?)
        """, [
            ("Return Policy", "Our return policy allows returns within 30 days of purchase for a full refund. The item must be unused and in its original packaging."),
            ("Shipping Times", "Standard shipping takes 3-5 business days. Expedited shipping takes 1-2 days. International shipping can take up to 14 days depending on customs."),
            ("Order Tracking", "Once your order ships, you will receive an email with a tracking number. You can also view the status by logging into your account and clicking 'Order History'."),
            ("Warranty Information", "All our electronic products come with a standard 1-year manufacturer warranty covering defects. Accidental damage is not covered."),
            ("Payment Methods", "We accept Visa, MasterCard, American Express, PayPal, and Apple Pay. Payments are securely processed using Stripe."),
            ("How to Contact Support", "If you need human assistance, you can use the Chat with AI feature or email support@sentimentflow.com. Our operating hours are 9 AM - 5 PM EST.")
        ])
        
    # Mock Data for Customers & Orders
    cursor.execute("SELECT COUNT(*) FROM Orders")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Customers (customer_id, name, email) VALUES (?, ?, ?)
        """, [
            ("CUST-001", "Alice Smith", "alice@example.com"),
            ("CUST-002", "Bob Johnson", "bob@example.com")
        ])
        
        cursor.executemany("""
            INSERT INTO Orders (order_id, customer_id, product_name, purchase_date, amount) VALUES (?, ?, ?, ?, ?)
        """, [
            ("ORD-101", "CUST-001", "Wireless Earbuds", "2026-04-10", 49.99),
            ("ORD-102", "CUST-002", "Smart Watch", "2026-04-12", 199.99),
            ("ORD-103", "CUST-001", "Gaming Mouse", "2026-04-15", 79.99),
            ("ORD-104", "CUST-002", "Mechanical Keyboard", "2026-04-18", 129.99),
            ("ORD-105", "CUST-001", "Webcam 4K", "2026-04-20", 99.99)
        ])
        
        # Insert Mock Tickets
        cursor.executemany("""
            INSERT INTO Tickets (customer_id, order_id, message, sentiment, urgency_level, suggested_action, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'New', ?)
        """, [
            ("CUST-001", "ORD-101", "My earbuds are completely broken out of the box!", "Angry", 9, "REFUND_OFFER", datetime.now().isoformat()),
            ("CUST-002", "ORD-104", "The keyboard is missing keycaps.", "Frustrated", 6, "ESCALATE", datetime.now().isoformat())
        ])
        
    # Mock Data for Feedback
    cursor.execute("SELECT COUNT(*) FROM Feedback")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Feedback (customer_id, message, sentiment_score, suggested_action, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("CUST-001", "The new layout is fantastic and very fast!", "Positive", "", datetime.now().isoformat()),
            ("CUST-002", "I found the documentation a bit hard to navigate.", "Negative", "Improve documentation search and add more top-level categories.", datetime.now().isoformat()),
            ("CUST-003", "Service was okay, nothing special.", "Neutral", "", datetime.now().isoformat())
        ])
    
    conn.commit()
    conn.close()

def create_ticket(customer_id, order_id, message, sentiment, urgency_level, suggested_action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Tickets (customer_id, order_id, message, sentiment, urgency_level, suggested_action, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'New', ?)
    """, (customer_id, order_id, message, sentiment, urgency_level, suggested_action, datetime.now().isoformat()))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def get_tickets():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tickets ORDER BY created_at DESC")
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets

def update_ticket_status(ticket_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()

def check_transaction(order_id):
    if not order_id:
        return None
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_feedback(customer_id, message, sentiment_score, suggested_action=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Feedback (customer_id, message, sentiment_score, suggested_action, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, message, sentiment_score, suggested_action, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Feedback ORDER BY created_at DESC")
    feedbacks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return feedbacks

def update_feedback_action(feedback_id, new_action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Feedback SET suggested_action = ? WHERE id = ?", (new_action, feedback_id))
    conn.commit()
    conn.close()

def get_all_faqs():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_base")
    faqs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return faqs

def create_todo(task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Todos (task, status, created_at)
        VALUES (?, 'Pending', ?)
    """, (task, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_todos():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Todos ORDER BY created_at DESC")
    todos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return todos

def update_todo_status(todo_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Todos SET status = ? WHERE id = ?", (status, todo_id))
    conn.commit()
    conn.close()

# Initialize db on module load
init_db()
