import streamlit as st
import requests
import re

# Central API URL for the FastAPI backend
API_URL = "http://localhost:8000"

st.set_page_config(page_title="SentimentFlow AI", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# CUSTOM CSS FOR PREMIUM AESTHETICS
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
            /* Base dark mode adjustments & typography */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Metric Cards Styling (Glassmorphism + Neon Accents) */
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(23, 25, 35, 0.8) 0%, rgba(13, 14, 21, 0.9) 100%);
                border: 1px solid rgba(139, 92, 246, 0.3); /* Amethyst Purple Accent */
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 20px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            [data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.2);
            }
            [data-testid="stMetricLabel"] {
                color: #A78BFA !important; /* Lighter Purple */
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-size: 0.85rem;
            }
            [data-testid="stMetricValue"] {
                color: #FFFFFF !important;
                font-size: 2rem !important;
                font-weight: 700;
            }

            /* Chat Bubbles */
            .stChatMessage {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                padding: 10px;
                margin-bottom: 10px;
                border-left: 3px solid #8B5CF6;
            }

            /* Expanders */
            .streamlit-expanderHeader {
                font-weight: 600;
                background-color: rgba(255, 255, 255, 0.02);
                border-radius: 8px;
            }
            
            /* Buttons */
            button[kind="primary"] {
                background: linear-gradient(90deg, #8B5CF6 0%, #6D28D9 100%) !important;
                border: none !important;
                box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
                font-weight: 600 !important;
                color: white !important;
                letter-spacing: 0.5px;
            }
            button[kind="primary"]:hover {
                box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6) !important;
                transform: scale(1.02);
            }
            
            /* Action Buttons in Hero Section */
            .action-button button {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                font-size: 1.4rem !important;
                border-radius: 15px !important;
                background: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(139, 92, 246, 0.5) !important;
                color: white !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                margin-bottom: 20px !important;
            }
            .action-button button:hover {
                background: rgba(139, 92, 246, 0.2) !important;
                border-color: #8B5CF6 !important;
                transform: translateY(-5px) !important;
            }
            
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# STATE MANAGEMENT
# ==========================================
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "customer_page" not in st.session_state:
    st.session_state.customer_page = "Home"
if "admin_page" not in st.session_state:
    st.session_state.admin_page = "Dashboard"



# ==========================================
# SIDEBAR: LOGIN & STATUS
# ==========================================
with st.sidebar:
    st.title("SentimentFlow 🌊")
    st.markdown("---")
    
    if not st.session_state.is_authenticated:
        st.subheader("Admin Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                if username == "admin" and password == "umhack26":
                    st.session_state.is_authenticated = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    else:
        st.subheader("Admin Controls")
        if st.button("Logout"):
            st.session_state.is_authenticated = False
            st.rerun()
            
    st.markdown("---")
    st.subheader("System Status")
    
    try:
        health_res = requests.get(f"{API_URL}/", timeout=2)
        if health_res.status_code == 200:
            st.success("Backend: Online ✅")
        else:
            st.error("Backend: Offline ❌")
    except requests.exceptions.RequestException:
        st.error("Backend: Offline ❌")

# ==========================================
# MAIN VIEW ROUTING
# ==========================================
if st.session_state.is_authenticated:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    view = st.sidebar.radio("Select View:", ["Customer Portal", "Merchant Dashboard"], index=1)
else:
    view = "Customer Portal"

# ==========================================
# VIEW: CUSTOMER PORTAL
# ==========================================
if view == "Customer Portal":
    
    # -------- SUB-PAGE ROUTING --------
    if st.session_state.customer_page == "Home":
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 3.5rem; background: -webkit-linear-gradient(45deg, #A78BFA, #6D28D9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>How can we help you?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 1.2rem; margin-bottom: 50px;'>Select an option below to get started.</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='action-button'>", unsafe_allow_html=True)
            if st.button("🚨\n\nFile a Complaint", use_container_width=True):
                st.session_state.customer_page = "Complaint"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='action-button'>", unsafe_allow_html=True)
            if st.button("💡\n\nProvide Feedback", use_container_width=True):
                st.session_state.customer_page = "Feedback"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='action-button'>", unsafe_allow_html=True)
            if st.button("📄\n\nSee Documentations", use_container_width=True):
                st.session_state.customer_page = "Docs"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='action-button'>", unsafe_allow_html=True)
            if st.button("💬\n\nChat with AI", use_container_width=True):
                st.session_state.customer_page = "Chat"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # -------- COMPLAINT PAGE --------
    elif st.session_state.customer_page == "Complaint":
        if st.button("⬅️ Back to Home"):
            st.session_state.customer_page = "Home"
            st.rerun()
            
        st.title("File a Complaint 🚨")
        st.write("Please provide your order details and the nature of your complaint. We'll escalate it immediately.")
        
        with st.form("complaint_form", clear_on_submit=False):
            order_id = st.text_input("Order ID (e.g., ORD-101) *", help="This field is strictly required.")
            message = st.text_area("What seems to be the problem? *")
            submitted = st.form_submit_button("Submit Complaint", type="primary")
            
            if submitted:
                if not order_id.strip():
                    st.error("❌ Order ID is strictly required to file a complaint.")
                elif not message.strip():
                    st.error("❌ Please provide a description of the problem.")
                else:
                    with st.spinner("Processing..."):
                        try:
                            res = requests.post(f"{API_URL}/process", json={
                                "message": f"I am filing a complaint. {message}",
                                "customer_id": "CUST-001",
                                "order_id": order_id
                            })
                            if res.status_code == 200:
                                data = res.json().get("data", {})
                                ticket_id = data.get("ticket_id")
                                if ticket_id:
                                    st.success(f"Complaint successfully filed! Ticket #{ticket_id} has been created.")
                                else:
                                    # Fallback to AI response string if it failed strict validation inside the brain
                                    st.warning(data.get("response_text", "Failed to create ticket. Is your Order ID valid?"))
                            else:
                                st.error("System error. Please try again later.")
                        except:
                            st.error("Failed to connect to backend.")

    # -------- FEEDBACK PAGE --------
    elif st.session_state.customer_page == "Feedback":
        if st.button("⬅️ Back to Home"):
            st.session_state.customer_page = "Home"
            st.rerun()
            
        st.title("Provide Feedback 💡")
        st.write("We are constantly looking to improve. Let us know how we did!")
        
        with st.form("feedback_form", clear_on_submit=True):
            message = st.text_area("Your Feedback")
            submitted = st.form_submit_button("Submit Feedback", type="primary")
            
            if submitted and message:
                with st.spinner("Analyzing and saving..."):
                    try:
                        res = requests.post(f"{API_URL}/feedback", json={"message": message, "customer_id": "CUST-001"})
                        if res.status_code == 200:
                            st.success("Thank you for your valuable feedback!")
                        else:
                            st.error("Failed to save feedback.")
                    except:
                        st.error("Failed to connect to backend.")

    # -------- DOCUMENTATION PAGE --------
    elif st.session_state.customer_page == "Docs":
        if st.button("⬅️ Back to Home"):
            st.session_state.customer_page = "Home"
            st.rerun()
            
        st.title("Documentations & FAQs 📄")
        
        try:
            res = requests.get(f"{API_URL}/faqs", timeout=5)
            if res.status_code == 200:
                faqs = res.json()
                for faq in faqs:
                    with st.expander(f"📌 {faq['topic'].replace('_', ' ').title()}"):
                        st.write(faq['answer'])
            else:
                st.error("Failed to fetch documents.")
        except:
            st.error("System offline.")

    # -------- CHAT PAGE --------
    elif st.session_state.customer_page == "Chat":
        if st.button("⬅️ Back to Home"):
            st.session_state.customer_page = "Home"
            st.rerun()
            
        st.title("Chat with AI 💬")
        st.write("I am capable of filing complaints, recording feedback, and providing documentation natively!")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Type your message here..."):
            extracted_order_id = None
            match = re.search(r"ORD-\d+", prompt)
            if match:
                extracted_order_id = match.group(0)

            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(f"{API_URL}/process", json={
                        "message": prompt,
                        "customer_id": "CUST-001",
                        "order_id": extracted_order_id
                    }, timeout=15)
                    
                    if response.status_code == 200:
                        result = response.json()
                        data = result.get("data", {})
                        
                        if result.get("is_ambiguous"):
                            bot_response = data.get("response_text", "Could you provide more details?")
                        elif result.get("type") == "enquiry":
                            bot_response = data.get("response_text", "Here is your answer...")
                        else:
                            ticket_id = data.get("ticket_id")
                            ack = data.get("response_text", "I apologize for the frustration. I have escalated this.")
                            if ticket_id:
                                bot_response = f"{ack}\n\n✅ **Ticket #{ticket_id} Created**"
                            else:
                                bot_response = ack
                    else:
                        bot_response = "The AI is currently deep in thought. Please try again in a moment or contact manual support."
                except Exception as e:
                    bot_response = "The AI is currently deep in thought. Please try again in a moment or contact manual support."

            with st.chat_message("assistant"):
                st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})



# ==========================================
# VIEW: MERCHANT DASHBOARD
# ==========================================
elif view == "Merchant Dashboard" and st.session_state.is_authenticated:
    
    if st.session_state.admin_page == "Dashboard":
        st.title("Merchant Dashboard ⚙️")
        
        # Create the three requested tabs
        tab1, tab2, tab3 = st.tabs(["📋 Complaint Management", "📊 Feedback Sentiment Analysis", "📝 To-do"])

        # -------- TAB 1: COMPLAINTS --------
        with tab1:
            st.markdown("<p style='color: #9CA3AF; font-size: 1.1rem;'>Review escalated complaints. Action is required.</p>", unsafe_allow_html=True)
            try:
                response = requests.get(f"{API_URL}/tickets", timeout=5)
                if response.status_code == 200:
                    tickets = response.json()
                    if not tickets:
                        st.info("No tickets found.")
                    else:
                        open_tickets = sorted(
                            [t for t in tickets if t["status"] == "New"],
                            key=lambda x: (-x.get("urgency_level", 0), x.get("created_at", ""))
                        )
                        st.markdown("### Open Complaints")
                        if not open_tickets:
                            st.success("All complaints have been resolved!")
                        else:
                            for ticket in open_tickets:
                                verification_status = "Verified Order ✅" if ticket.get("order_id") else "ID Mismatch / Missing ❌"
                                
                                # Removed sentiment from expander header per user request
                                with st.expander(f"Ticket #{ticket['ticket_id']} - Urgency: {ticket['urgency_level']}/10 ({ticket['created_at'][:10]})"):
                                    st.write(f"**Customer ID:** {ticket['customer_id']}")
                                    st.write(f"**Order ID:** {ticket['order_id']}")
                                    st.write(f"**Verification Status:** {verification_status}")
                                    st.write(f"**Message:** {ticket['message']}")
                                    
                                    # Removed Sentiment Score metric per user request, only showing Urgency
                                    st.metric("Urgency Level", f"{ticket['urgency_level']}/10")
                                        
                                    st.write(f"**Suggested Action:** `{ticket['suggested_action']}`")
                                    
                                    if st.button(f"Approve & Resolve: {ticket['suggested_action']}", key=f"approve_{ticket['ticket_id']}", type="primary"):
                                        res = requests.patch(f"{API_URL}/tickets/{ticket['ticket_id']}", json={"status": "Resolved"}, timeout=5)
                                        if res.status_code == 200:
                                            st.success("Ticket resolved!")
                                            st.rerun()
                                            
                        st.markdown("---")
                        if st.button("View Resolved Complaints", type="secondary"):
                            st.session_state.admin_page = "Resolved_Complaints"
                            st.rerun()
                else:
                    st.error("Failed to fetch tickets from the backend.")
            except Exception as e:
                st.error("The AI is currently deep in thought. Please try again in a moment or contact manual support.")

        # -------- TAB 2: FEEDBACK SENTIMENT --------
        with tab2:
            st.markdown("<p style='color: #9CA3AF; font-size: 1.1rem;'>AI-driven analysis of customer feedback.</p>", unsafe_allow_html=True)
            try:
                fb_response = requests.get(f"{API_URL}/feedback", timeout=5)
                if fb_response.status_code == 200:
                    feedbacks = fb_response.json()
                    if not feedbacks:
                        st.info("No feedback has been collected yet.")
                    else:
                        # Calculate sentiment distribution
                        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
                        for fb in feedbacks:
                            score = fb.get("sentiment_score", "Neutral")
                            if score in sentiment_counts:
                                sentiment_counts[score] += 1
                                
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Positive Feedback", f"{sentiment_counts['Positive']}")
                        with col2:
                            st.metric("Neutral Feedback", f"{sentiment_counts['Neutral']}")
                        with col3:
                            st.metric("Negative Feedback", f"{sentiment_counts['Negative']}")
                        
                        st.markdown("---")
                        
                        # Display a pseudo-bar chart using Streamlit's native st.bar_chart
                        st.markdown("### Sentiment Breakdown")
                        st.bar_chart(sentiment_counts)
                        
                        st.markdown("### Suggested Actions Based on Feedback")
                        actions_found = False
                        for fb in feedbacks:
                            action = fb.get("suggested_action", "")
                            if action:
                                actions_found = True
                                with st.container():
                                    st.info(f"💡 {action}")
                                    col1, col2 = st.columns([1, 1])
                                    with col1:
                                        if st.button("Approve", key=f"app_fb_{fb['id']}", type="primary", use_container_width=True):
                                            requests.patch(f"{API_URL}/feedback/{fb['id']}", json={"suggested_action": ""}, timeout=5)
                                            requests.post(f"{API_URL}/todos", json={"task": action}, timeout=5)
                                            st.success("Added to To-do list!")
                                            st.rerun()
                                    with col2:
                                        if st.button("Reject", key=f"rej_fb_{fb['id']}", use_container_width=True):
                                            requests.patch(f"{API_URL}/feedback/{fb['id']}", json={"suggested_action": ""}, timeout=5)
                                            st.rerun()
                        
                        if not actions_found:
                            st.write("No actionable items found.")
                            
                        st.markdown("---")
                        if st.button("View Raw Feedback Log", type="primary"):
                            st.session_state.admin_page = "Raw_Feedback"
                            st.rerun()
                            
                else:
                    st.error("Failed to fetch feedback from the backend.")
            except Exception as e:
                st.error("The AI is currently deep in thought. Please try again in a moment or contact manual support.")
                
        # -------- TAB 3: TO-DO --------
        with tab3:
            st.markdown("<p style='color: #9CA3AF; font-size: 1.1rem;'>Manage your actionable tasks.</p>", unsafe_allow_html=True)
            
            # Form to add new todo
            with st.form("add_todo_form", clear_on_submit=True):
                new_task = st.text_input("New Task")
                submitted = st.form_submit_button("Add Task")
                if submitted and new_task:
                    try:
                        requests.post(f"{API_URL}/todos", json={"task": new_task}, timeout=5)
                        st.success("Task added!")
                        st.rerun()
                    except:
                        st.error("Failed to add task.")
            
            st.markdown("### Open Tasks")
            try:
                todo_response = requests.get(f"{API_URL}/todos", timeout=5)
                if todo_response.status_code == 200:
                    todos = todo_response.json()
                    open_todos = [t for t in todos if t["status"] == "Pending"]
                    
                    if not open_todos:
                        st.info("No pending tasks. Great job!")
                    else:
                        for t in open_todos:
                            # Use checkbox
                            is_checked = st.checkbox(t["task"], key=f"todo_{t['id']}")
                            if is_checked:
                                requests.patch(f"{API_URL}/todos/{t['id']}", json={"status": "Completed"}, timeout=5)
                                st.success("Task marked as completed!")
                                st.rerun()
                                
                    st.markdown("---")
                    if st.button("View Completed Tasks", type="secondary"):
                        st.session_state.admin_page = "Completed_Todos"
                        st.rerun()
                else:
                    st.error("Failed to fetch tasks.")
            except Exception as e:
                st.error("Could not connect to the backend.")

    elif st.session_state.admin_page == "Raw_Feedback":
        st.title("Raw Feedback Log 📝")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.admin_page = "Dashboard"
            st.rerun()
            
        try:
            fb_response = requests.get(f"{API_URL}/feedback", timeout=5)
            if fb_response.status_code == 200:
                feedbacks = fb_response.json()
                if not feedbacks:
                    st.info("No feedback has been collected yet.")
                else:
                    for fb in feedbacks:
                        score = fb.get("sentiment_score", "Neutral")
                        action = fb.get("suggested_action", "")
                        # Add a quick emoji indicator based on score
                        emoji = "🟢" if score == "Positive" else "🟡" if score == "Neutral" else "🔴"
                        with st.expander(f"{emoji} {score} - Customer: {fb['customer_id']} ({fb['created_at'][:10]})"):
                            st.write(f"**Feedback:** {fb['message']}")
                            if action:
                                st.write(f"**Suggested Action:** {action}")
            else:
                st.error("Failed to fetch feedback from the backend.")
        except Exception as e:
            st.error("The AI is currently deep in thought. Please try again in a moment or contact manual support.")
            
    elif st.session_state.admin_page == "Resolved_Complaints":
        st.title("Resolved Complaints 📁")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.admin_page = "Dashboard"
            st.rerun()
            
        try:
            response = requests.get(f"{API_URL}/tickets", timeout=5)
            if response.status_code == 200:
                tickets = response.json()
                resolved_tickets = sorted(
                    [t for t in tickets if t["status"] == "Resolved"],
                    key=lambda x: x.get("created_at", ""),
                    reverse=True
                )
                if not resolved_tickets:
                    st.info("No resolved complaints found.")
                else:
                    for ticket in resolved_tickets:
                        with st.expander(f"Ticket #{ticket['ticket_id']} - Resolved ({ticket['created_at'][:10]})"):
                            st.write(f"**Customer ID:** {ticket['customer_id']}")
                            st.write(f"**Order ID:** {ticket['order_id']}")
                            st.write(f"**Message:** {ticket['message']}")
                            st.write(f"**Action Taken:** {ticket['suggested_action']}")
            else:
                st.error("Failed to fetch tickets from the backend.")
        except Exception as e:
            st.error("The AI is currently deep in thought. Please try again in a moment or contact manual support.")
            
    elif st.session_state.admin_page == "Completed_Todos":
        st.title("Completed Tasks 🗂️")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.admin_page = "Dashboard"
            st.rerun()
            
        try:
            todo_response = requests.get(f"{API_URL}/todos", timeout=5)
            if todo_response.status_code == 200:
                todos = todo_response.json()
                completed_todos = [t for t in todos if t["status"] == "Completed"]
                
                if not completed_todos:
                    st.info("No completed tasks yet.")
                else:
                    for t in completed_todos:
                        st.markdown(f"✅ ~~{t['task']}~~ *(Completed)*")
            else:
                st.error("Failed to fetch tasks from the backend.")
        except Exception as e:
            st.error("The AI is currently deep in thought. Please try again in a moment or contact manual support.")
