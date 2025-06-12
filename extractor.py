import os
import json
import re
import google.generativeai as genai
import pdfplumber
from dotenv import load_dotenv
from collections import OrderedDict
from PIL import Image
import pytesseract

# Specify path to the Tesseract executable (especially on macOS with Homebrew)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"


#  Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#  Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="Extract invoice fields exactly as shown. Preserve all field names. Never infer. Keep all keys even if empty or null."
)

def clean_json_output(text):
    start_index = text.find('{')
    end_index = text.rfind('}')
    if start_index == -1 or end_index == -1:
        return text
    json_string = text[start_index:end_index + 1]
    json_string = json_string.replace('\\"', '"').replace('\\n', '').replace('\\t', '').replace('\\r', '')
    json_string = json_string.replace('None', 'null')
    json_string = re.sub(r',\s*([}\]])', r'\1', json_string)
    return json_string

def extract_text_from_file(file_path):
    if file_path.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or '' for page in pdf.pages)
        except:
            return ""
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            return pytesseract.image_to_string(Image.open(file_path))
        except:
            return ""
    return ""

def extract_data_from_pdf_gemini(file_path):
    try:
        text = extract_text_from_file(file_path)

        if not text.strip():
            return {"error": "No text extracted from PDF."}

        # Prompt to you file Format
        prompt = f"""
You are a document parsing assistant. From the following shipping document text, extract the fields below into this **exact JSON structure**.

 Very Strict Instructions:
- DO NOT rename any keys.
- Set missing values as "" or null.
- Use the actual words from the scanned document.
- Keep the structure intact even if fields are blank.

{{
  "Header": [
    {{
      "BillOfLadingNo": "",
      "BillOfLadingDate": "",
      "VesselName": "",
      "VoyageNo": "",
      "PortOfDestination": "",
      "PortOfLoading": "",
      "ShipperName": "",
      "ShipperAdd1": "",
      "ShipperAdd2": "",
      "ShipperAdd3": "",
      "ConsigneeName": "",
      "ConsigneeAdd1": "",
      "ConsigneeAdd2": "",
      "ConsigneeAdd3": "",
      "NotifyPartyName": "",
      "NotifyPartyAdd1": "",
      "NotifyPartyAdd2": "",
      "NotifyPartyAdd3": ""
    }}
  ],
  "ItemsDetails": [
    {{
      "ContainerNo": "",
      "ISO": "",
      "Liner": "",
      "CargoDescription": "",
      "NoOfPackages": "",
      "Unit": "",
      "GrossWeight": "",
      "NetWeight": "",
      "SealNo": ""
    }}
  ]
}}

Here is the extracted document text:
{text}
"""

        response = model.generate_content(prompt)
        raw_output = response.text
        cleaned_output = clean_json_output(raw_output)
        data = json.loads(cleaned_output)

        return data

    except json.JSONDecodeError as e:
        return {"error": f"JSON decoding failed: {e}", "raw_output": raw_output}
    except Exception as e:
        return {"error": str(e)}
