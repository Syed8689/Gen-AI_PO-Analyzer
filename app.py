import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
 
st.title("GenAI Observation & Risk Extractor (Free via Together AI)")
 
together_api_key = st.secrets.get("TOGETHER_API_KEY")
 
if not together_api_key:
    st.error("❌ Together AI API key not found. Please add it under Streamlit Secrets.")
    st.stop()
 
uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
 
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif file.name.lower().endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""
 
def analyze_text_with_together(text, api_key):
    prompt = f"""
Consider yourself as a IT Cost Optimization specialist, expert is Application portfloio rationalization. Based on Purchase Orders and Sales Order documents uploaded, extract:
 
- PO start Date
- PO end date
- PO Quantity and OUM
- PO signatory
- Clause
- PO Amount

 
Return it in markdown table format with rows: PO Start Date, PO End Date, PO Signatory, PO Quantity, Clause 
 
Text to analyze:
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
        "max_tokens": 1024
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {res.status_code} - {res.text}"
 
if uploaded_file:
    with st.spinner("Extracting and analyzing..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No readable text found in the document.")
        else:
            output = analyze_text_with_together(text, together_api_key)
            st.markdown(output)
