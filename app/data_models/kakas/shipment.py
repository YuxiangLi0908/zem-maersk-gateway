"""Models for Kaka Sheng shipment ordering."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator


class KakasOrderAddressBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    detailOne: Annotated[str, StringConstraints(min_length=1, max_length=2048)]
    detailTwo: Annotated[str, StringConstraints(max_length=2048)] | None = None
    city: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    state: str
    country: str
    postCode: str
    contacts: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    telephone: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    email: Annotated[str, StringConstraints(min_length=3, max_length=255)]
    remark: Annotated[str, StringConstraints(max_length=30)] | None = None
    remarkExt: Annotated[str, StringConstraints(max_length=100)] | None = None
    clientNo: str | None = None
    clientRefNo: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("email must be a valid email address")
        return value


class KakasOrderOrigin(KakasOrderAddressBase):
    stockupTime: str
    pickupTimeBegin: str
    pickupTimeEnd: str

    @field_validator("stockupTime", "pickupTimeBegin", "pickupTimeEnd")
    @classmethod
    def validate_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("time must be in HH:mm format") from exc
        return value


class KakasOrderDestination(KakasOrderAddressBase):
    deliveryTime: str
    deliveryTimeBegin: str
    deliveryTimeEnd: str

    @field_validator("deliveryTime")
    @classmethod
    def validate_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("deliveryTime must be in yyyy-MM-dd format") from exc
        return value

    @field_validator("deliveryTimeBegin", "deliveryTimeEnd")
    @classmethod
    def validate_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("time must be in HH:mm format") from exc
        return value


class KakasInsurance(BaseModel):
    insureAmount: Annotated[float, Field(gt=0)]


class KakasShipmentCreateRequest(BaseModel):
    uuid: str
    rateId: str
    originalMsg: KakasOrderOrigin
    destinationMsg: KakasOrderDestination
    insurance: KakasInsurance | None = None
    customerDump: Literal[0, 1] | None = None
