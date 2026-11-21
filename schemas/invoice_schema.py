# the data structure i want the output of llm to follow strictly along with data validation in runtime

from unittest.mock import Base

from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date


class InvoiceData(BaseModel):

    vendor_name: str | None = Field(alias="Vendor Name")

    vendor_address: str | None = Field(alias="Vendor Address")

    customer_name: str | None = Field(alias="Customer Name")

    customer_address: str | None = Field(alias="Customer Address")

    invoice_number: str | None = Field(alias="Invoice Number")

    order_number: str | None = Field(alias="Order Number")

    invoice_date: date | None = Field(alias="Invoice Date")

    due_date: date | None = Field(alias="Due Date")

    subtotal: float | None = Field(alias="Subtotal")

    tax_amount: float | None = Field(alias="Tax Amount")

    tax_type: str | None = Field(alias="Tax Type")

    total_amount: float | None = Field(alias="Total Amount")

    payment_status: str | None = Field(alias="Payment Status")

    discounts: float | None = Field(alias="Discounts")

    shipping_charge: float | None = Field(alias="Shipping / Delivery Charge")

    service_charge: float | None = Field(alias="Service Charge")

    @field_validator(
        "subtotal",
        "tax_amount",
        "discounts",
        "shipping_charge",
        "service_charge",
        "total_amount"
    )
    @classmethod
    def validate_amounts(cls,value):
        if value is not None and value<0:
            raise ValueError('invoice amounts cant be negative')
        return value


    @model_validator(mode='after')
    def validate_invoice(self):
        # check subtotal+tax=total

        amounts=[
            self.subtotal,
            self.tax_amount,
            self.discounts,
            self.shipping_charge,
            self.service_charge,
            self.total_amount
        ]

        if all( amount is not None for amount in amounts):
            calculated_total=self.subtotal-self.discounts+self.shipping_charge+self.service_charge+self.tax_amount

            if abs(calculated_total-self.total_amount)>0.01:
                raise ValueError('Invoice total does not match calculated total')

        # check invoice date and due date

        if self.invoice_date is not None and self.due_date is not None:

            if self.due_date < self.invoice_date:

                raise ValueError(
                    "Due date cannot be earlier than invoice date"
                )

        return self

class FieldAssessment(BaseModel):

    confidence: float = Field(ge=0, le=1)

    evidence: str | None

    reason: str

class InvoiceAssessment(BaseModel):
    fields:dict[str,FieldAssessment]

