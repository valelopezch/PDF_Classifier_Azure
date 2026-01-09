import streamlit as st
import pandas as pd
from pypdf import PdfReader
import re
from collections import defaultdict
from tools import classify_document

st.set_page_config(page_title="Document Consult", page_icon="🧠", layout="wide")

st.title("🎯 Welcome to your PDF document consult")

# AUXILIAR FUNCTIONS

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages_text = []

    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    full_text = "\n".join(pages_text)
    return full_text

def clean_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()
    return text

def truncate_text(text, max_chars = 12000):
    if len(text) <= max_chars:
        return text
    return text[:max_chars]

PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE": r"\b(\+?\d{1,3})?\s?\d{3}\s?\d{3}\s?\d{4}\b",
    "ID": r"\b(CC|TI|NIT)\s?\d{6,12}\b",
    "PERSON": r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+\b"
}


def pseudonymize_text(text):
    counters = defaultdict(int)
    entity_map = {}

    def replace(entity_type, match):
        value = match.group(0)
        if value not in entity_map:
            counters[entity_type] += 1
            entity_map[value] = f"[{entity_type}_{counters[entity_type]}]"
        return entity_map[value]

    for entity_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, lambda m: replace(entity_type, m), text)

    return text, entity_map

# MAIN CODE

uploaded_file = st.file_uploader(
    "📄 Upload a PDF document",
    type=["pdf"]
)
if uploaded_file is not None:
    with st.spinner("Processing document..."):

        try:
            # 1. Extract text
            raw_text = extract_text_from_pdf(uploaded_file)

            if not raw_text.strip():
                st.error("❌ Could not extract text from this PDF.")
                st.stop()

            # 2. Preprocess
            cleaned_text = clean_text(raw_text)
            truncated_text = truncate_text(cleaned_text)

            # 3. Pseudonymize
            masked_text, pii_map = pseudonymize_text(truncated_text)

            # 4. Classify
            result = classify_document(masked_text)

        except Exception as e:
            st.error(f"❌ Error processing document: {e}")
            st.stop()

    st.success("✅ Document processed successfully")

    st.subheader("📌 Classification Result")
    st.markdown(f"**Category:** `{result.category}`")
    st.markdown(f"**Justification:** {result.justification}")