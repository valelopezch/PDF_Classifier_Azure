# PDF Document Classification with Azure OpenAI

This project implements an automatic PDF document classification system using Large Language Models (LLMs) deployed in Azure OpenAI.

The system classifies documents into one of the following categories:
- Contrato
- Queja o Reclamo
- Resolución administrativa
- Informe técnico
- Comunicación interna
- Otros

In addition to the classification, the model generates a short textual justification explaining the decision.

---

## 🚀 Features

- PDF text extraction
- Basic text normalization
- Pseudonymization of sensitive data (PII) before model inference
- Deterministic LLM behavior (temperature = 0)
- Structured JSON output validated with Pydantic
- Interactive Streamlit interface
- Secure handling of Azure OpenAI credentials
