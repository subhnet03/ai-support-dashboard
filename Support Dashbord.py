import gradio as gr
import pandas as pd
from datetime import datetime

# GOOGLE SHEET (AUTO REFRESH)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1968LlPseIAttkVXkkAb5s4X87q-jlioh22Lf8c71hGo/export?format=csv"

def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df["Created_Date"] = pd.to_datetime(df["Created_Date"], errors="coerce")
        df["Status"] = df["Status"].astype(str)
        df["Urgency"] = df["Urgency"].astype(str)
        df["Issue_Type"] = df["Issue_Type"].astype(str)
        return df
    except:
        return pd.DataFrame()


# SUMMARY CARDS

def generate_summary():
    df = load_data()
    if df.empty:
        return "<h3 style='color:red;'>Unable to load data</h3>"

    total = len(df)
    open_tickets = df[df["Status"].str.lower()=="open"].shape[0]
    closed_tickets = df[df["Status"].str.lower()=="closed"].shape[0]
    high = df[df["Urgency"].str.lower()=="high"].shape[0]
    top_issue = df["Issue_Type"].value_counts().idxmax()

    return f"""
    <div style="background:#111827;padding:30px;border-radius:20px;color:white;margin-top:30px">
        <h2>📌 Quick Insights</h2>
        <p><b>Total Tickets:</b> {total}</p>
        <p><b>Open Tickets:</b> {open_tickets}</p>
        <p><b>Closed Tickets:</b> {closed_tickets}</p>
        <p><b>High Priority:</b> {high}</p>
        <p><b>Top Issue Type:</b> {top_issue}</p>
    </div>
    """


# SMART CHATBOT (Dynamic)

def answer_question(message, history):
    df = load_data()
    if df.empty:
        return "Data not available."

    q = message.lower()

    try:
        if "least" in q:
            issue = df["Issue_Type"].value_counts().idxmin()
            count = df["Issue_Type"].value_counts().min()
            return f"Least reported issue: {issue} ({count} tickets)"

        if "most" in q or "highest" in q:
            issue = df["Issue_Type"].value_counts().idxmax()
            count = df["Issue_Type"].value_counts().max()
            return f"Most reported issue: {issue} ({count} tickets)"

        if "open" in q:
            return f"Open tickets: {df[df['Status'].str.lower()=='open'].shape[0]}"

        if "closed" in q:
            return f"Closed tickets: {df[df['Status'].str.lower()=='closed'].shape[0]}"

        if "high" in q:
            return f"High urgency tickets: {df[df['Urgency'].str.lower()=='high'].shape[0]}"

        if "month" in q:
            this_month = datetime.now().month
            count = df[df["Created_Date"].dt.month == this_month].shape[0]
            return f"Tickets created this month: {count}"

        if "total" in q:
            return f"Total tickets: {len(df)}"

        # Generic logical summary
        return f"There are {len(df)} total tickets across {df['Issue_Type'].nunique()} issue types."

    except:
        return "I couldn't process that question. Please try again."


# UI LAYOUT (PROPER SCROLL FIX)

with gr.Blocks(theme=gr.themes.Soft()) as demo:

    # GLOBAL CSS FIX
    gr.HTML("""
    <style>
        body {overflow-y:auto !important;}
        .gradio-container {max-width:100% !important;}
        iframe {width:100%; border:none;}
    </style>
    """)

    gr.Markdown("# 📊 AI Customer Support Dashboard")

    
    gr.HTML("""
    <iframe 
        src="https://lookerstudio.google.com/embed/reporting/7df8c60a-f8a6-4d65-b12d-b89c0c2f48c2/page/LBJoF"
        height="900">
    </iframe>
    """)

    gr.HTML(generate_summary())

    gr.Markdown("## 🤖 Ask Dashboard Assistant")

    gr.ChatInterface(answer_question)

demo.launch()

