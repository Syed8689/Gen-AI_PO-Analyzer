import streamlit as st
import requests
import fitz  # For PDFs
import docx  # For DOCX files

st.title("🧾 GenAI-Based PO Analyzer (Phase 1) – Application Portfolio Rationalization")

# Load Together AI API key
together_api_key = st.secrets.get("TOGETHER_API_KEY")
if not together_api_key:
    st.error("❌ API key not found. Please add it under Streamlit Secrets.")
    st.stop()

# Upload PO File
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

A Purchase Order (PO) document has been uploaded. Extract and return a structured summary in **Markdown Table Format** with the following headers:

| PO Start Date | PO End Date | Quantity & UOM | PO Price | PO Description | PO Signatory | PO Contract Tenure | PO Clause Summary |
|---------------|-------------|----------------|----------|----------------|--------------|---------------------|-------------------|

---

**Field Extraction Rules:**

1. **PO Start Date / PO End Date**
   - These are the official PO validity dates.
   - If multiple dates are found, prioritize main PO validity dates.

2. **Quantity & UOM**
   - Total number with unit (e.g., 340 NOS)

3. **PO Price (Incl. GST & Currency)**
   - Mention the full amount including taxes.
   - Clearly state the currency: USD or INR (e.g., USD 1,000 or INR 12,50,000)

4. **PO Description**
   - Start with the application/product name (e.g., '{po_name}')
   - Then add a short summary of modules, services, licenses covered.
   - Do not use <br>. Use plain markdown line breaks if needed.

5. **PO Signatory**
   - Extract name or designation of the person signing the PO.
   - Usually found under “For [Company Name]”. If not present, write "Not Mentioned" — though it's typically included.

6. **PO Contract Tenure**
   - Extract Contract Start and End Dates (if explicitly mentioned).
   - Calculate duration (e.g., "3-year contract").
   - If contract duration is not found, write: “Contract tenure not mentioned”.

7. **PO Clause Summary**
   - Present this section as numbered bullet points (1, 2, 3...).
   - Extract from any “PO Terms”, “Special Terms”, “General Terms” sections.
   - Include important clauses such as:
     - Payment Terms (e.g., payment must be made within 30/45/90 days or penalties apply)
     - Early Termination Rights (e.g., PO/licensing can be cancelled with 45-day notice)
     - Unlimited Usage or transfer clauses
     - Risk clauses: non-cancellable PO, lock-in conditions, penalty provisions

---

**Guidelines:**
- Thoroughly analyze the entire document and extract data for **all 8 columns**.
- Do not skip or summarize generically.
- Return only a Markdown Table.
- Remove all <br> from output.

---

Here is the PO text:
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
        content = response.json()["choices"][0]["message"]["content"]
        return content.replace("<br>", " ").strip()
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# Run app
if uploaded_file:
    with st.spinner("🔍 Analyzing uploaded PO for contract terms and risks..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No readable text found in the uploaded file.")
        else:
            result = analyze_po(text, together_api_key, uploaded_file.name)
            st.markdown(result)
