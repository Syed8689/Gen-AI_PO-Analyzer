import streamlit as st
import requests
import fitz  # PyMuPDF for PDFs
import docx  # For DOCX files

st.title("GenAI-Based PO Analyzer for Application Portfolio Rationalization (Phase 1)")

# Load Together AI API key
together_api_key = st.secrets.get("TOGETHER_API_KEY")
if not together_api_key:
    st.error("❌ API key not found. Please add it in Streamlit Secrets.")
    st.stop()

# Upload PO File
uploaded_file = st.file_uploader("📤 Upload a PO file (PDF or DOCX)", type=["pdf", "docx"])

# File text extraction function
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif file.name.lower().endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

# GenAI-powered PO analyzer
def analyze_po(text, api_key, po_filename):
    po_name = po_filename.replace("_", " ").replace(".pdf", "").replace(".docx", "").strip()
    prompt = f"""
You are an AI assistant with expertise in IT Cost Optimization and Application Portfolio Rationalization.

A Purchase Order (PO) has been uploaded. Please extract and return a structured summary using the following fields in Markdown Table format:

| PO Start Date | PO End Date | Quantity & UOM | PO Price (Incl. GST & Currency) | PO Description | PO Signatory | PO Clause Summary |
|---------------|-------------|----------------|-----------------------|----------------|---------------|----------------------|

**Field Requirements:**

1. **PO Start Date and PO End Date** – Extract accurately from the PO.
2. **Quantity & UOM** – Extract numeric quantity and Unit of Measure from the PO.
3. **PO Price (Incl. GST & Currency)** – Include total price with tax and clearly state the currency (e.g., INR, USD).
4. **PO Description** – Start with the application/product name (e.g., '{po_name}') followed by module/subscription/service description.
5. **PO Signatory** – Name of authorized signatory from vendor or purchaser.
6. **PO Clause Summary** – Present as bullet points numbered 1, 2, 3… Include the following if available:
   - Payment terms (e.g., 30/45/90 days, penalties)
   - Early termination rights (e.g., cancel with 45-day notice)
   - Unlimited usage terms (e.g., license linked to employee count)
   - License reassignment or transferability
   - Bundling or co-termination terms
   - Risk clauses or any non-cancellable condition
   - If both PO duration and Contract duration are available, clearly distinguish and display both inside this clause summary

Only respond using a clean **Markdown Table** with no HTML tags. No commentary or explanation.

---
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

# Execute analysis on uploaded file
if uploaded_file:
    with st.spinner("🔍 Analyzing PO for key fields and clauses..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No readable text found in the uploaded file.")
        else:
            result = analyze_po(text, together_api_key, uploaded_file.name)
            st.markdown(result)
