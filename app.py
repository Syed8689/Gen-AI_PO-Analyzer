import streamlit as st
import requests
import fitz  # PyMuPDF for PDF parsing
import docx  # python-docx for DOCX parsing

st.title("GenAI-Based PO Analyzer for Application Portfolio Rationalization (Phase 1)")

# Load API key
together_api_key = st.secrets.get("TOGETHER_API_KEY")
if not together_api_key:
    st.error("❌ API key not found. Please add it in Streamlit Secrets.")
    st.stop()

# Upload PO File
uploaded_file = st.file_uploader("📤 Upload a PO file (PDF or DOCX)", type=["pdf", "docx"])

# File text extraction
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif file.name.lower().endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

# Call Together AI to analyze PO
def analyze_po(text, api_key):
    prompt = f"""
You are an AI assistant with expertise in IT Cost Optimization and Application Portfolio Rationalization.

A user has uploaded a Purchase Order (PO) or a Sales Order (SO). Extract and return the following structured information in a markdown table:

- PO Start Date  
- PO End Date  
- PO Quantity and Unit of Measure (UOM)  
- PO Total Price (including GST if available)  
- PO Description (modules, services, licenses)  
- PO Signatory  
- PO Clauses (summarize clearly, highlight risks and special terms such as):  
  • Payment terms (e.g., payment within 30/45/90 days or fines if delayed)  
  • Cancellation clauses (e.g., customer may terminate with 45 days notice)  
  • Unlimited usage terms based on employee base  
  • License transferability or bundling  

Respond **only** with a Markdown Table using the following columns:
| PO Start Date | PO End Date | Quantity & UOM | PO Price (Incl. GST) | PO Description | PO Signatory | PO Clauses Summary |
|---------------|-------------|----------------|-----------------------|----------------|---------------|----------------------|

Here is the PO content:
{text}
"""

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# Execution
if uploaded_file:
    with st.spinner("🔍 Analyzing PO for key terms and clauses..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No readable text found in the uploaded file.")
        else:
            result = analyze_po(text, together_api_key)
            st.markdown(result)
