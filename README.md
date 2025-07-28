A lightweight Streamlit app to extract PO start date, PO end date, PO quantity & OUM, PO signatory, PO Amount, Cluase from uploaded PDF or DOCX documents using Together AI's free Mixtral-8x7B-Instruct model.
⚙️ Features
Upload PDF or DOCX files
Extracts text using PyMuPDF or python-docx
Sends prompt to Together AI to generate:
PO start date
Renders results in a clean markdown table
🧱 Tech Stack
LLM: Together AI – Mixtral-8x7B-Instruct
Frontend: Streamlit
Parsing: PyMuPDF, python-docx
Hosting: Streamlit Cloud (Free)
🔐 Setup Instructions
Upload app.py and requirements.txt to a GitHub repo
Deploy via Streamlit Cloud
In Streamlit Secrets, add:
tomlCopyEdit
