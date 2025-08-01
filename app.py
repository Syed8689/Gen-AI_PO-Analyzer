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
You are an AI assistant specializing in IT Cost Optimization and Application Portfolio Rationalization.

A Purchase Order (PO) document has been uploaded. Extract and return a structured summary using the Markdown Table format with the following headers:

| PO Start Date | PO End Date | Quantity & UOM | PO Price | PO Description | PO Signatory | PO Clause Summary |
|---------------|-------------|----------------|-------------------------------|----------------|---------------|----------------------|

---

**Field Extraction Rules:**

1. **PO Start Date / End Date**  
   - Identify official PO duration (if multiple are present, choose primary duration or indicate both clearly).  

2. **Quantity & UOM**  
   - Total quantity and its Unit of Measure (e.g., 340 NOS)

3. **PO Price**  
   - Mention amount inclusive of tax. Highlight currency clearly: INR or USD.

4. **PO Description**  
   - Start with the PO name or reference (e.g., 'LinkedIn Sales Navigator')  
   - Followed by a short explanation of modules or licenses subscribed  
   - Do **not use <br>**, instead use real line breaks

5. **PO Signatory**  
   - Extract the **authorized signatory name or title** from the bottom of the PO  


6. **PO Clause Summary**  
   - Present clauses as numbered bullet points (1, 2, 3...)  
   - Extract important clauses including:  
     - Payment terms (e.g., payment within 30/45/90 days, penalties)  
     - Early termination rights (e.g., customer may terminate with 45-day notice)  
     - Unlimited usage terms or license transferability  
     - Risk clauses (non-cancellable, lock-in, penalty clauses)  
     - Mention if there’s a Contract Duration **separate from PO Duration**  
   - Keep the summary clean. No <br>. Each point must appear in a new line.

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
