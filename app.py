import streamlit as st
import requests
import fitz  # For PDFs
import docx  # For DOCX files

st.title("🧾 GenAI-Based PO Analyzer (Phase 1) – Application Portfolio Rationalization")

# Load Together AI API key from Streamlit Secrets
together_api_key = st.secrets.get("TOGETHER_API_KEY")
if not together_api_key:
    st.error("❌ API key not found. Please add it under Streamlit Secrets.")
    st.stop()

# File upload
uploaded_file = st.file_uploader("📤 Upload a PO file (PDF or DOCX)", type=["pdf", "docx"])

# Extract text from PDF or DOCX
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif file.name.lower().endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

# Analyze the text using Together AI
def analyze_po(text, api_key, po_filename):
    po_name = po_filename.replace("_", " ").replace(".pdf", "").replace(".docx", "").strip()

    prompt = f"""You are a GenAI assistant specializing in IT Cost Optimization and Application Portfolio Rationalization.

A Purchase Order (PO) has been uploaded. Extract and return a structured summary in **Markdown Table Format** with the following headers:

| PO Start Date | PO End Date | Quantity & UOM | PO Price | PO Description | PO Signatory | PO Contract Tenure | PO Clause Summary |
|---------------|-------------|----------------|----------------------------------|----------------|--------------|---------------------|-------------------|

---

**Field Extraction Rules:**

1. **PO Start Date / PO End Date**  
   - These are the official PO validity dates.
   - If multiple dates are found, prioritize main PO validity dates.

2. **Quantity & UOM**  
   - E.g., 340 NOS

3. **PO Price (Incl. GST & Currency)**  
   - Mention the total value including tax and state currency clearly (e.g., USD 1,000 or INR 12,50,000).

4. **PO Description**  
   - Start with the name of the PO or application (e.g., '{po_name}').  
   - Then add a short explanation of the modules or licenses subscribed.  
   - Avoid using <br>. Use real markdown newlines if needed.

5. **PO Signatory**  
   - Extract the name/title of the authorized signatory from the PO.  
   - This is usually found near “For [Company Name]” at the bottom of the document.

6. **PO Contract Tenure**  
   - Extract Contract Start Date and Contract End Date (if available).  
   - Calculate duration (e.g., “3-year contract”)  
   - If contract duration isn't explicitly written, mention “Contract tenure not mentioned”.

7. **PO Clause Summary**  
   - Present this as bullet points (numbered 1, 2, 3...).  
   - Extract from any “PO Terms”, “Special Terms”, or “General Terms” section.  
   - Include any of the following if found:
     - Payment Terms (e.g., payment must be made within 45 days of PO generation or penalties apply)
     - Early Termination Rights (e.g., customer may terminate the PO or license with 45 days' notice)
     - Unlimited Usage Terms (e.g., license is unlimited based on employee headcount)
     - Risk Clauses (e.g., PO is non-cancellable, has lock-in, or penalties)

---

Do not use <br> anywhere in the output. Output must be formatted as a Markdown Table only with no commentary.

Here is the extracted PO content:
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

# Trigger analysis after upload
if uploaded_file:
    with st.spinner("🔍 Analyzing uploaded PO for contract terms and risks..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No readable text found in the uploaded file.")
        else:
            result = analyze_po(text, together_api_key, uploaded_file.name)
            st.markdown(result)
