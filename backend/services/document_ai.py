"""
Google Document AI service — processes uploaded tax documents (W-2, 1099, etc.)
and returns structured extracted fields.
"""
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
import os, json
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID   = os.getenv("GOOGLE_PROJECT_ID")
LOCATION     = os.getenv("GOOGLE_LOCATION", "us")
PROCESSOR_ID = os.getenv("GOOGLE_PROCESSOR_ID")

def get_client():
    opts = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
    return documentai.DocumentProcessorServiceClient(client_options=opts)

def process_document(file_bytes: bytes, mime_type: str = "application/pdf") -> dict:
    """
    Send raw bytes to Document AI and return extracted key-value pairs.
    """
    client = get_client()
    name   = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    raw_doc  = documentai.RawDocument(content=file_bytes, mime_type=mime_type)
    request  = documentai.ProcessRequest(name=name, raw_document=raw_doc)
    result   = client.process_document(request=request)
    document = result.document

    extracted = {}

    # ── Form fields (key-value pairs) ─────────────────────────────
    for page in document.pages:
        for field in page.form_fields:
            key_text   = field.field_name.text_anchor.content  if field.field_name.text_anchor.content  else ""
            value_text = field.field_value.text_anchor.content if field.field_value.text_anchor.content else ""
            extracted[key_text.strip()] = value_text.strip()

    # ── Named entities (if processor supports them) ───────────────
    entities = {}
    for entity in document.entities:
        entities[entity.type_] = entity.mention_text

    return {
        "raw_text":   document.text[:2000],   # first 2k chars for AI context
        "form_fields": extracted,
        "entities":   entities,
        "doc_type":   _infer_doc_type(document.text, entities),
    }

def _infer_doc_type(text: str, entities: dict) -> str:
    text_lower = text.lower()
    if "w-2" in text_lower or "wage and tax statement" in text_lower:
        return "W2"
    if "1099" in text_lower:
        return "1099"
    if "1098" in text_lower:
        return "1098"
    if "mortgage" in text_lower:
        return "1098"
    return "other"

def extract_tax_fields(extracted: dict) -> dict:
    """
    Normalize raw Document AI output into standardised tax fields.
    """
    fields = extracted.get("form_fields", {})
    entities = extracted.get("entities", {})

    def find(*keys):
        for k in keys:
            for field_key, val in fields.items():
                if k.lower() in field_key.lower():
                    return val
            if k in entities:
                return entities[k]
        return None

    return {
        "employer_name":     find("employer", "Employer's name"),
        "employee_name":     find("employee", "Employee's name"),
        "wages":             find("wages", "Box 1", "1 Wages"),
        "federal_tax_withheld": find("federal income tax", "Box 2", "2 Federal"),
        "state_tax_withheld":   find("state income tax", "Box 17"),
        "social_security_wages": find("social security wages", "Box 3"),
        "medicare_wages":    find("medicare wages", "Box 5"),
        "payer_name":        find("payer", "Payer's name"),
        "nonemployee_compensation": find("nonemployee", "Box 7"),
        "interest_income":   find("interest income", "Box 1"),
        "dividends":         find("ordinary dividends", "Box 1a"),
    }
