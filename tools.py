from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import os
from openai import AzureOpenAI
import httpx
from apikey import subscription_key, api_version, endpoint

model_name = "gpt-4o-mini"
deployment = "doc-classifier-gpt4o-mini"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

class ClassificationResponse(BaseModel):
    category: str = Field(
        ..., 
        description="One of: Contrato, Queja o Reclamo, Resolución, Informe técnico, Comunicación interna"
    )
    justification: str = Field(
        ..., 
        description="2–3 sentence explanation citing textual evidence"
    )

parser = PydanticOutputParser(pydantic_object=ClassificationResponse)

def classify_document(text: str) -> ClassificationResponse:
    format_instructions = parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "You are an AI system designed to classify administrative and technical documents.\n\n"
            "Classify the document into EXACTLY ONE of the following categories:\n"
            "1. Contrato\n"
            "2. Queja o Reclamo\n"
            "3. Resolución\n"
            "4. Informe técnico\n"
            "5. Comunicación interna\n\n"
            "Definitions:\n"
            "- Contrato: Legal or formal agreements defining obligations, duration, and terms.\n"
            "- Queja o Reclamo: Expressions of dissatisfaction, complaints, or requests for correction.\n"
            "- Resolución: Official decisions issued by an authority that resolve a matter.\n"
            "- Informe técnico: Technical or analytical documents presenting results, evaluations, or recommendations.\n"
            "- Comunicación interna: Internal memos, emails, or notices intended for internal organizational use.\n\n"
            "Respond ONLY with a JSON object following this format:\n"
            "{format_instructions}\n\n"
            "Document:\n"
            "{text}"
        ),
        input_variables=["text"],
        partial_variables={"format_instructions": format_instructions},
    )

    final_prompt = prompt.format(text=text)

    response = client.chat.completions.create(
        model = deployment, 
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise document classification system. "
                    "Follow the instructions strictly. "
                    "Do not add any extra fields."
                )
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        temperature=0,
        max_tokens=500
    )

    raw_output = response.choices[0].message.content

    return parser.parse(raw_output)