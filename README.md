
# 📄 Smart Document Intelligence System

An AI-powered document processing application that extracts, validates, and structures information from PDF documents using Large Language Models (LLMs), LangChain, and Pydantic.

The project currently focuses on **automated invoice information extraction**, with the goal of extending it to resumes, reports, contracts, and other recurring PDF document types.

Instead of manually reading documents and transferring information into spreadsheets, the application automates the process of converting unstructured PDF content into structured, validated, and reusable data.

---

## 🚀 Overview

Traditional document processing involves manually reading PDFs, identifying relevant information, and organizing it into structured formats.

Smart Document Intelligence automates this workflow using an LLM-powered extraction pipeline.

For invoices, the application extracts information such as:

- Vendor and customer details
- Invoice and order numbers
- Invoice and due dates
- Subtotal and tax amount
- Tax type
- Discounts
- Shipping and delivery charges
- Service charges
- Total amount
- Payment status

The extracted information is validated using Pydantic, assessed for confidence, and presented for human review before being exported.

---

## ✨ Features

### 1. PDF Text Extraction
- Load PDF documents using LangChain's `PyPDFLoader`.
- Extract text from individual pages.
- Combine extracted content for downstream processing.
- Support multi-page PDFs containing selectable text.

### 2. LLM-Based Information Extraction
- Use Groq-hosted LLMs for information extraction.
- Convert unstructured document text into structured JSON.
- Extract predefined fields using task-specific prompts.
- Avoid inventing information when fields are unavailable.

### 3. Structured Output with Pydantic
- Define structured data schemas using Pydantic.
- Validate extracted field types.
- Handle optional and missing information.
- Use field aliases to maintain readable output keys.

### 4. Custom Data Validation
- Validate individual monetary fields.
- Prevent negative monetary values.
- Verify invoice total calculations.
- Validate invoice and due dates.
- Detect inconsistencies in extracted information.

### 5. Error Handling and Retry Mechanism
- Handle malformed JSON responses.
- Handle Pydantic validation errors.
- Retry failed extraction attempts.
- Provide previous validation errors as feedback to the LLM.

### 6. Confidence Assessment
- Evaluate extracted fields against the original document.
- Generate confidence estimates for individual fields.
- Identify potentially unreliable or ambiguous information.
- Provide supporting evidence and explanations.

*Note: LLM-generated confidence scores are estimates and are not statistically calibrated probabilities.*

### 7. Human-in-the-Loop Review
- Review extracted invoice information.
- Inspect confidence estimates and supporting evidence.
- Identify fields requiring manual attention.
- Correct extracted values.
- Revalidate corrected information before acceptance.

### 8. Batch PDF Processing
- Automatically discover PDF files inside the documents directory.
- Process multiple invoices in a single execution.
- Maintain separate processing results.
- Continue processing when an individual document fails.
- Generate a batch processing summary.

### 9. Data Export
Export accepted invoice information into:

- **JSON:** Structured data for applications and API integrations.
- **CSV:** Spreadsheet-compatible data for analysis.
- **Consolidated CSV:** A combined record of successfully processed invoices.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| LangChain | LLM integration and PDF document loading |
| Groq | LLM inference |
| GPT-OSS-120B | Information extraction and assessment |
| Pydantic | Structured output and data validation |
| PyPDF | PDF text extraction |
| python-dotenv | Environment variable management |
| JSON | Structured data export |
| CSV | Tabular data export |
| Streamlit | User interface development |

---

## 🏗️ Application Architecture

The application follows a modular document-processing pipeline:

```text
                 PDF Documents
                       |
                       v
               PDF Text Extraction
                       |
                       v
             LLM Information Extraction
                       |
                       v
               Structured JSON Output
                       |
                       v
               Pydantic Validation
                       |
                       v
              Custom Data Validation
                       |
                       v
              Confidence Assessment
                       |
                       v
              Human-in-the-Loop Review
                       |
                       v
                Final Validation
                       |
                       v
                 Data Export
                       |
              +--------+--------+
              |                 |
              v                 v
          JSON Export       CSV Export
                                |
                                v
                       Consolidated CSV
```

### Batch Processing

The batch-processing component discovers PDF files and independently executes the document-processing pipeline for each file.

```text
Documents Folder
       |
       v
  Batch Processor
       |
       +---------- Invoice 1
       |                |
       |                v
       |         Extraction Pipeline
       |                |
       |                v
       |          JSON / CSV
       |
       +---------- Invoice 2
       |                |
       |                v
       |         Extraction Pipeline
       |                |
       |                v
       |          JSON / CSV
       |
       +---------- Invoice 3
                        |
                        v
                 Extraction Pipeline
                        |
                        v
                   JSON / CSV

       |
       v
Consolidated CSV
```

---

## 📁 Project Structure

```text
document_intelligence/
│
├── documents/
│   ├── gstinvoice.pdf
│   ├── multipageinvoice.pdf
│   └── sample_invoice.pdf
│
├── outputs/
│   ├── gstinvoice.json
│   ├── gstinvoice.csv
│   ├── sample_invoice.json
│   ├── sample_invoice.csv
│   └── all_invoices.csv
│
├── schemas/
│   └── invoice_schema.py
│
├── src/
│   └── document_intelligence/
│       └── __init__.py
│
├── app.py
├── main.py
├── config.toml
├── requirements.txt
├── pyproject.toml
├── .env
├── .gitignore
└── README.md
```

### Directory Description

| File / Directory | Description |
|---|---|
| `documents/` | Stores input PDF documents |
| `outputs/` | Stores extracted JSON and CSV files |
| `schemas/` | Contains Pydantic data models |
| `src/` | Package structure for future modular development |
| `main.py` | Main Python processing pipeline |
| `app.py` | Streamlit application entry point |
| `config.toml` | Application configuration |
| `.env` | Stores API credentials |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Project configuration and package metadata |

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/document-intelligence.git

cd document-intelligence
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Alternatively, install the core dependencies:

```bash
pip install langchain-community langchain-groq pypdf pydantic python-dotenv
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
```

Obtain your API key from:

https://console.groq.com/keys

Make sure `.env` is included in `.gitignore` and never commit your API credentials to GitHub.

### 5. Add PDF Documents

Place your invoice PDFs inside the `documents/` directory.

Example:

```text
documents/
├── invoice_001.pdf
├── invoice_002.pdf
└── invoice_003.pdf
```

---

## ▶️ Running the Application

### Run the Python Processing Pipeline

Execute:

```bash
python main.py
```

The application will:

1. Discover PDF files in the documents directory.
2. Extract text from each document.
3. Send the extracted content to the LLM.
4. Generate structured invoice information.
5. Validate the extracted data.
6. Assess extraction confidence.
7. Request human review and corrections.
8. Export accepted invoices.
9. Generate a consolidated CSV.

### Running the Streamlit Interface

If using the Streamlit interface:

```bash
streamlit run app.py
```

The interface can be used as the entry point for interacting with the document-processing pipeline.

---

## 📤 Output Examples

### JSON Output

```json
{
    "Vendor Name": "DEMO - Sliced Invoices",
    "Vendor Address": "123 Somewhere Street",
    "Customer Name": "Test Business",
    "Customer Address": "Melbourne, VIC 3000",
    "Invoice Number": "INV-3337",
    "Order Number": "12345",
    "Invoice Date": "2016-01-25",
    "Due Date": "2016-01-31",
    "Subtotal": 85.0,
    "Tax Amount": 8.5,
    "Tax Type": null,
    "Discounts": 0.0,
    "Shipping / Delivery Charge": 0.0,
    "Service Charge": 0.0,
    "Total Amount": 93.5,
    "Payment Status": "Paid"
}
```

*Example output. Actual extracted values depend on the input invoice.*

### Consolidated CSV

| Source File | Invoice Number | Vendor Name | Total Amount |
|---|---|---|---:|
| invoice_001.pdf | INV-3337 | DEMO - Sliced Invoices | 93.50 |
| invoice_002.pdf | INV-3338 | ABC Technologies | 150.00 |

---

## 🔍 Current Limitations

- Currently optimized for invoice information extraction.
- PDF text extraction works with selectable-text PDFs; scanned documents require OCR support.
- Extraction accuracy depends on document quality and LLM performance.
- LLM-generated confidence scores are estimates and require calibration.
- Human review is currently terminal-based in the Python pipeline.
- Complex invoice calculations involving multiple tax rates, tax-inclusive pricing, and different discount rules require additional business validation.
- Batch processing currently handles documents sequentially.

---

## 🗺️ Future Roadmap

The long-term goal is to extend this project into a general-purpose AI document intelligence system.

### Phase 1: Invoice Intelligence
- [x] PDF text extraction
- [x] LLM-based information extraction
- [x] Pydantic structured schemas
- [x] Custom validation rules
- [x] Error handling and retries
- [x] Confidence assessment
- [x] Human-in-the-loop review
- [x] JSON and CSV exports
- [x] Multiple invoice processing

### Phase 2: User Interface
- [ ] Streamlit-based document upload
- [ ] Interactive extraction dashboard
- [ ] Editable extracted fields
- [ ] Visual confidence indicators
- [ ] Human approval workflow
- [ ] Downloadable JSON and CSV outputs
- [ ] Batch processing dashboard

### Phase 3: Multi-Document Intelligence
- [ ] Resume information extraction
- [ ] Candidate profile generation
- [ ] Skills and experience extraction
- [ ] Report summarization and information extraction
- [ ] Contract information extraction
- [ ] Document-specific Pydantic schemas
- [ ] Automatic document-type identification

### Phase 4: Advanced AI Capabilities
- [ ] OCR integration for scanned PDFs
- [ ] Advanced document understanding
- [ ] Improved extraction verification
- [ ] Source-level evidence and field traceability
- [ ] More robust confidence assessment
- [ ] Intelligent document classification
- [ ] Agentic workflows for complex document processing

### Phase 5: Production Readiness
- [ ] Persistent database storage
- [ ] User authentication
- [ ] Processing history
- [ ] Background document processing
- [ ] API integration
- [ ] Deployment and monitoring

---

## 💡 Project Vision

The long-term vision is to build a unified document intelligence platform that can understand different types of documents and dynamically extract relevant information based on their structure and purpose.

Rather than building separate applications for invoices, resumes, reports, and contracts, the goal is to develop a reusable document-processing architecture with document-specific schemas, extraction instructions, and validation rules.

**Upload a document → Understand its content → Extract structured information → Validate → Review → Export.**

---

## 👨‍💻 Author

**Chirag Agrawal**

B.Tech, Information Technology

GitHub: https://github.com/your-username

---

*Built with Python, LangChain, Pydantic, and Groq.*
