
from schemas.invoice_schema import InvoiceData
from pydantic import ValidationError


sample_data = {

    "Vendor Name": "DEMO - Sliced Invoices",

    "Vendor Address": "123 Somewhere Street",

    "Customer Name": "Test Business",

    "Customer Address": "Melbourne, VIC",

    "Invoice Number": "INV-3337",

    "Order Number": "12345",

    "Invoice Date": "2016-01-25",

    "Due Date": "2016-01-31",

    "Subtotal": 85.00,

    "Tax Amount": 8.50,

    "Tax Type": None,

    "Discounts": 0.00,

    "Shipping / Delivery Charge": 0.00,

    "Service Charge": 0.00,

    "Total Amount": 93.50,

    "Payment Status": "Paid"
}


try:

    result = InvoiceData.model_validate(sample_data)

    print("Invoice validation successful!")
    print(result.model_dump(by_alias=True))

except ValidationError as e:

    print("Invoice validation failed!")
    print(e)
