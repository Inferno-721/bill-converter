from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date


# -----------------------------
# Seller Details
# -----------------------------
class Seller(BaseModel):
    name: str
    address: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None


# -----------------------------
# Customer Details
# -----------------------------
class Customer(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    gst: Optional[str] = None
    dl_no: Optional[str] = None


# -----------------------------
# Invoice Metadata
# -----------------------------
class InvoiceMeta(BaseModel):
    invoice_number: str
    invoice_date: date
    invoice_group: Optional[str] = None


# -----------------------------
# Line Item
# -----------------------------
class InvoiceItem(BaseModel):
    part_name: str
    hsn_code: Optional[str] = None
    batch_no: Optional[str] = None
    expiry: Optional[str] = None
    mrp: Optional[float] = 0.0
    qty: float
    free_qty: Optional[float] = 0.0
    rate: float
    amount: float
    gst_percent: Optional[float] = 0.0

    @field_validator("qty", "rate", "amount")
    @classmethod
    def must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Numeric fields must be positive")
        return v


# -----------------------------
# Totals
# -----------------------------
class InvoiceTotals(BaseModel):
    basic_total: Optional[float] = 0.0
    discount_total: Optional[float] = 0.0
    taxable_total: float
    invoice_total: float
    invoice_total_words: Optional[str] = None

    @field_validator("invoice_total")
    @classmethod
    def total_must_be_valid(cls, v):
        if v < 0:
            raise ValueError("Invoice total cannot be negative")
        return v


# -----------------------------
# Bank Details
# -----------------------------
class BankDetails(BaseModel):
    bank_name: Optional[str] = None
    account_name: Optional[str] = None
    ifsc: Optional[str] = None
    account_no: Optional[str] = None
    upi: Optional[str] = None


# -----------------------------
# Full Invoice Schema
# -----------------------------
class Invoice(BaseModel):
    seller: Seller
    customer: Customer
    invoice_meta: InvoiceMeta
    items: List[InvoiceItem]
    totals: InvoiceTotals
    bank_details: Optional[BankDetails] = None

    @property
    def computed_total(self) -> float:
        """
        Dynamically compute total from items.
        Useful for validation.
        """
        return sum(item.amount for item in self.items)

    def validate_totals(self):
        """
        Cross-check extracted total with computed total.
        """
        computed = round(self.computed_total, 2)
        extracted = round(self.totals.invoice_total, 2)

        if computed != extracted:
            raise ValueError(
                f"Total mismatch: computed={computed}, extracted={extracted}"
            )
