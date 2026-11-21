# i will load the pdf (invoice, resume, ....) and then extract text out of it 

from email.mime import base
import time
import traceback
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import csv
# STEP 1 - PDF Loading and returning langchain Document Structure
def load_document(pdf_path:str):
    base_dir=Path(__file__).resolve().parent
    pdf_path=base_dir/pdf_path # absolute path :)
    loader=PyPDFLoader(str(pdf_path))
    document=loader.load()
    return document


# STEP 2 - Extracting Text and returning the text

def extract_text(document):

    extracted_text='\n'

    for page in document:
        extracted_text+=page.page_content+'\n'
    return extracted_text





# STEP 3 - Integrating LLM - we want the LLM to taje the entire text and give it in a structured format 

import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


llm=ChatGroq(
    model='openai/gpt-oss-120b',
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY')
)


'''def extract_invoice_information(text):

    prompt=f"""
    You are an expert invoice information extraction system.

    Analyze the following invoice and extract these fields:

    1. Vendor Name
    2. Vendor Address
    3. Customer Name
    4. Customer Address
    5. Invoice Number
    6. Order Number
    7. Invoice Date
    8. Due Date
    9. Subtotal
    10. Tax Amount
    11. Tax Type
    12. Total Amount
    13. Payment Status

    Instructions:

    - Extract information only from the provided invoice.
    - Do not invent or assume missing information.
    - If a field is unavailable, return null.
    - Return monetary values as numbers without currency symbols.
    - Return the output in valid JSON format.
    - Do not include markdown formatting or explanations.
    

    Invoice Content:

    {text}
    """

    response=llm.invoke(prompt)
    return response.content'''


# STEP 4 - Integrate Pydantic and update the extract info function

import json
from pydantic import ValidationError
from schemas.invoice_schema import InvoiceData

def extract_invoice_information(text):
    prompt=f"""
    You are an expert invoice information extraction system.

    Analyze the following invoice and extract these fields:

    1. Vendor Name
    2. Vendor Address
    3. Customer Name
    4. Customer Address
    5. Invoice Number
    6. Order Number
    7. Invoice Date
    8. Due Date
    9. Subtotal
    10. Tax Amount
    11. Tax Type
    12. Total Amount
    13. Payment Status
    14. Discounts
    15. Shipping / Delivery Charge
    16. Service Charge

    Instructions:

    - Extract information only from the provided invoice.
    - Do not invent or assume missing information.
    - If a field is unavailable, return null.
    - Return monetary values as numbers without currency symbols.
    - Return the output in valid JSON format.
    - Do not include markdown formatting or explanations.
    - Return Invoice Date and Due Date in YYYY-MM-DD format.
    - Extract Discounts as the actual monetary discount amount.
    - If only a discount percentage is mentioned and the monetary
      discount cannot be determined, return null.
    - Extract Shipping / Delivery Charge separately.
    - Extract Service Charge separately.
    - Do not include these charges in Subtotal if they are
      separately listed.
    - Return 0 only when the invoice explicitly indicates
      that a charge or discount is zero.
    - Do not assume Tax Type if it is not explicitly mentioned.

    Invoice Content:

    {text}
    """

    
    max_retries = 5

    for attempt in range(max_retries):

        try:

            print(f"\nExtraction attempt: {attempt + 1}")

            response = llm.invoke(prompt)

            extracted_data = json.loads(response.content)

            validated_data = InvoiceData.model_validate(extracted_data)

            print("Invoice extraction successful!")

            return validated_data


        except json.JSONDecodeError as e:

            print("Error: Invalid JSON received.")

            prompt += f"""

            Your previous response contained invalid JSON.

            JSON parsing error:
            {str(e)}

            Correct the JSON format and return valid JSON only.
            """


        except ValidationError as e:

            print("Error: Invoice validation failed.")

            prompt += f"""

            Your previous extracted data failed validation.

            Validation errors:
            {e}

            Re-examine the original invoice content and correct
            the extracted values. Do not invent missing information.

            Return valid JSON only.
            """


    raise ValueError("Invoice extraction failed after 3 attempts.")



from schemas.invoice_schema import InvoiceAssessment
# Step 7 - Confidence Assessment

def assess_invoice_confidence(text, invoice_data):

    prompt = f"""
    You are an invoice verification assistant.

    Your task is to assess the reliability of extracted
    invoice information against the original invoice.

    Original Invoice:

    {text}

    Extracted Invoice Information:

    {invoice_data.model_dump(by_alias=True)}

    For every extracted field, provide:

    1. Confidence score between 0 and 1.
    2. Evidence supporting the extracted value.
    3. Reason explaining the confidence score.

    Instructions:

    - Compare every extracted field against the original invoice.
    - Give higher confidence when information is explicitly
      present and clearly labelled.
    - Give lower confidence when information is ambiguous,
      incomplete or difficult to identify.
    - Do not invent supporting evidence.
    - If a field is null, assess whether its absence is
      consistent with the original invoice.
    - If an extracted field is null, evidence should also be null
      when no supporting text exists.
    - Explain why the field is unavailable in the reason.
    - Do not assign high confidence merely because a field is null.
    - Return an assessment for every extracted field.
    - Return valid JSON only.

    Expected JSON structure:

    {{
        "fields": {{
            "Invoice Number": {{
                "confidence": 0.99,
                "evidence": "Invoice Number INV-3337",
                "reason": "Clearly identified"
            }}
        }}
    }}
    """

    response = llm.invoke(prompt)

    assessment_data = json.loads(response.content)

    assessment = InvoiceAssessment.model_validate(assessment_data)

    return assessment



# Step 8 - Identify Fields Requiring Review

def identify_fields_for_review(assessment):

    review_fields = []

    for field_name, details in assessment.fields.items():

        if details.confidence < 0.80:

            review_fields.append(field_name)

    return review_fields


# STEP 9 - Human Review

def review_invoice(invoice_data, assessment):
    print("\n========== INVOICE REVIEW ==========\n")

    invoice_dict=invoice_data.model_dump(by_alias=True)

    for field_name, value in invoice_dict.items():
        details=assessment.fields.get(field_name)

        if details is None:
            print(f'{field_name}: {value}')
            print('confidence: not assessed\n')
            continue 

        print(f"{field_name}: {value}")

        print(f"Confidence: {details.confidence * 100:.1f}%")

        print(f"Evidence: {details.evidence}")

        print(f"Reason: {details.reason}")

        if details.confidence<0.80:
            print('REVIEW REQUIRED')
        print("-----------------------------------")


    review_fields=identify_fields_for_review(assessment)

    if review_fields:
        print('\nFields requiring manual review:')
        for field in review_fields:
            print(f'- {field}')

    else:
        print('\nNo fields flagged for review')

    choice=input(
        '\nDo you accept this extracted invoice? (yes/no):'
    ).strip().lower()


    if choice=='yes':
        print('\nInvoice accepted!')
        return invoice_data
    elif choice=='no':
        print("\nEnter corrections as a JSON object.")

        print('Example: {"Invoice Number": "INV-9999"}')

        corrections = input("\nCorrections: ")

        try:

            corrections = json.loads(corrections)

            updated_data = invoice_dict.copy()

            updated_data.update(corrections)

            corrected_invoice = InvoiceData.model_validate(updated_data)

            print("\nCorrected invoice successfully validated!")

            return corrected_invoice

        except (json.JSONDecodeError, ValidationError) as e:

            print("\nCorrection failed:")

            print(e)

            return None


    else:

        print("\nInvalid choice.")

        return None



# Step 9A - Individual JSON Export

def export_json(invoice_data, file_name):

    base_dir = Path(__file__).resolve().parent

    output_dir = base_dir / "outputs"

    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{file_name}.json"

    invoice_dict = invoice_data.model_dump(
        by_alias=True,
        mode="json"
    )

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(invoice_dict, file, indent=4)

    print(f"JSON exported: {output_path}")


# Step 9B - Individual CSV Export

def export_csv(invoice_data, file_name):

    base_dir = Path(__file__).resolve().parent

    output_dir = base_dir / "outputs"

    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{file_name}.csv"

    invoice_dict = invoice_data.model_dump(
        by_alias=True,
        mode="json"
    )

    with open(output_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=invoice_dict.keys()
        )

        writer.writeheader()

        writer.writerow(invoice_dict)

    print(f"CSV exported: {output_path}")


# Step 9C - Consolidated CSV Export

def export_consolidated_csv(invoice_records):

    base_dir = Path(__file__).resolve().parent

    output_dir = base_dir / "outputs"

    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "all_invoices.csv"

    if not invoice_records:

        print("\nNo accepted invoices to export.")

        return

    fieldnames = list(invoice_records[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(invoice_records)

    print(f"\nConsolidated CSV exported: {output_path}")




# Step 9D - Process One Invoice

def process_invoice(pdf_path):

    print("\n======================================")

    print(f"Processing: {pdf_path.name}")

    print("======================================")

    try:

        # Step 1 - Load PDF

        document = load_document(
            str(Path("documents") / pdf_path.name)
        )


        # Step 2 - Extract Text

        text = extract_text(document)


        # Step 3 - Extract Invoice Information

        result = extract_invoice_information(text)


        # Step 4 - Confidence Assessment

        assessment = assess_invoice_confidence(text, result)


        # Step 5 - Human Review

        final_invoice = review_invoice(result, assessment)


        if final_invoice is None:

            print(f"\nInvoice review incomplete: {pdf_path.name}")

            return None


        # Step 6 - Generate Unique Filename

        file_name = pdf_path.stem


        # Step 7 - Export Individual Files

        export_json(final_invoice, file_name)

        export_csv(final_invoice, file_name)


        # Step 8 - Prepare Record for Consolidated CSV

        invoice_dict = final_invoice.model_dump(
            by_alias=True,
            mode="json"
        )

        invoice_dict["Source File"] = pdf_path.name


        print(f"\nSuccessfully processed: {pdf_path.name}")

        return invoice_dict


    except Exception as e:

        print(f"\nFailed to process {pdf_path.name}")

        print(f"Reason: {e}")

        return None



# Step 9E - Batch Invoice Processing

def process_multiple_invoices():

    base_dir = Path(__file__).resolve().parent

    documents_dir = base_dir / "documents"

    pdf_files = sorted(documents_dir.glob("*.pdf"))

    if not pdf_files:

        print("\nNo PDF files found in documents folder.")

        return


    print(f"\nTotal invoices found: {len(pdf_files)}")


    accepted_invoices = []

    failed_invoices = []


    for index, pdf_path in enumerate(pdf_files, start=1):

        print(f"\n\nProcessing invoice {index}/{len(pdf_files)}")


        result = process_invoice(pdf_path)


        if result is not None:

            accepted_invoices.append(result)

        else:

            failed_invoices.append(pdf_path.name)


    # Export Consolidated CSV

    export_consolidated_csv(accepted_invoices)


    # Final Processing Summary

    print("\n========== BATCH PROCESSING SUMMARY ==========")

    print(f"Total invoices: {len(pdf_files)}")

    print(f"Successfully processed: {len(accepted_invoices)}")

    print(f"Failed invoices: {len(failed_invoices)}")


    if failed_invoices:

        print("\nFailed Documents:")

        for invoice in failed_invoices:

            print(f"- {invoice}")


    print("\nBatch processing completed!")








# STEP 5 - Running till now pipeline


# Step 10 - Running the Application

# Step 10 - Run Application

if __name__ == "__main__":

    process_multiple_invoices()

