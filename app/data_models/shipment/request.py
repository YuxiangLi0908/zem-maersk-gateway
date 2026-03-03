from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_serializer, field_validator


class ShipmentMonetary(BaseModel):
    declaredValue: Decimal
    isDeclaredValueInsurance: bool
    collectOnDeliveryAmount: Decimal
    commercialInvoiceValue: Decimal

    @field_validator(
        "declaredValue",
        "collectOnDeliveryAmount",
        "commercialInvoiceValue",
        mode="before",
    )
    @classmethod
    def validate_money_two_decimals(cls, value) -> Decimal:
        try:
            d = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValueError("monetary fields must be numeric") from e

        q = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if d != q:
            raise ValueError("monetary fields must have exactly 2 decimals")
        return q

    @field_serializer(
        "declaredValue",
        "collectOnDeliveryAmount",
        "commercialInvoiceValue",
        when_used="json",
    )
    def serialize_money(self, value: Decimal) -> float:
        return float(value)


class ShipmentAddress(BaseModel):
    name: str
    address1: str
    address2: Optional[str] = None
    city: str
    regionCode: Optional[str] = None
    postalCode: str
    countryCode: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class AccessorialsEnum(str, Enum):
    INSIDE = "Inside"
    HOTEL = "Hotel"
    LIFTGATE = "Liftgate"
    CONVENTION = "Convention"
    DEDICATED = "Dedicated"
    DEBRIS_REMOVAL = "DebrisRemoval"


class ShipmentParty(BaseModel):
    references: Optional[List[str]] = None
    accessorials: Optional[List[AccessorialsEnum]] = None
    address: ShipmentAddress


class ThirdParty(BaseModel):
    address: ShipmentAddress


class ShipmentLineItem(BaseModel):
    packaging: str
    pieces: int
    description: str
    weight: Decimal
    length: Decimal
    width: Decimal
    height: Decimal
    weightUnit: str
    dimensionalUnit: str

    @field_validator(
        "weight",
        "length",
        "width",
        "height",
        mode="before",
    )
    @classmethod
    def validate_money_two_decimals(cls, value) -> Decimal:
        try:
            d = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValueError("dim fields must be numeric") from e

        q = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if d != q:
            raise ValueError("dim fields must have exactly 2 decimals")
        return q

    @field_serializer(
        "weight",
        "length",
        "width",
        "height",
        when_used="json",
    )
    def serialize_money(self, value: Decimal) -> float:
        return float(value)


class ShipmentCreateRequest(BaseModel):
    tariffCode: Optional[str] = None
    locationId: Optional[int] = None
    controlStation: Optional[str] = None
    payType: Optional[str] = None
    specialInstructions: Optional[str] = None
    serviceCode: str
    shipDate: str
    shipReadyTime: str
    shipCloseTime: str

    monetary: Optional[ShipmentMonetary] = None
    thirdParty: Optional[ThirdParty] = None
    shipper: ShipmentParty
    consignee: ShipmentParty

    lineItems: List[ShipmentLineItem]

    @field_validator("shipDate")
    @classmethod
    def validate_ship_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError("shipDate must be in YYYY-MM-DD format") from e
        return value

    @field_validator("shipReadyTime", "shipCloseTime")
    @classmethod
    def validate_ship_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M:%S")
        except ValueError as e:
            raise ValueError("time must be in HH:MM:SS format") from e
        return value


class LabelRequest(BaseModel):
    shawb: str
    eLabelType: str
    szip: str


class BOLRequest(BaseModel):
    shawb: str
    szip: str
