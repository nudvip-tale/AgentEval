import os
from pypdf import PdfReader
import requests
from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.configs.app_config import settings

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def summarize_document(file_path, prompt=None):
    print("\n\ndocument tool called\n\n")
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
    client = setup_llm()
    summary_prompt = f"do the task :\n{text}"
    if prompt:
        summary_prompt += f"\nPrompt: {prompt}"
    response = client.invoke(summary_prompt)
    # print("\n\nResponse Generated\n\n")
    # print(response.content)
    return response.content