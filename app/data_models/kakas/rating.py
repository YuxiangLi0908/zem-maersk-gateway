"""Models for Kaka Sheng ``POST /shipment/quote``."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

PositiveInt = Annotated[int, Field(ge=1)]


class KakasTradeShowInfo(BaseModel):
    tradeshowName: str
    boothNo: str
    tradeshowDecorator: str
    entryTime: date


class KakasAddress(BaseModel):
    type: Literal[1, 2, 3]
    detailAddress: str | None = None
    city: str
    state: str
    postCode: str
    country: str = "US"
    serveIds: list[int] | None = None
    tradeshowInfo: KakasTradeShowInfo | None = None

    @model_validator(mode="after")
    def validate_trade_show(self):
        if self.serveIds and 8 in self.serveIds and self.tradeshowInfo is None:
            raise ValueError("tradeshowInfo is required when serveIds contains 8")
        return self


class KakasCommodity(BaseModel):
    describe: Annotated[str, StringConstraints(min_length=1)]
    commodityNum: PositiveInt
    commodityUnit: Annotated[int, Field(ge=1, le=14)]
    consignNum: PositiveInt
    palletType: Literal[1, 2]
    length: PositiveInt
    width: PositiveInt
    height: PositiveInt
    weight: PositiveInt
    declaredValue: PositiveInt
    freightClass: str
    nmfc: str | None = None
    nmfcSub: str | None = None
    commodityServerId: list[Literal[1, 2, 3, 4]] | None = None
    hazmatCode: str | None = None
    hazmatLevel: Annotated[str, StringConstraints(pattern=r"^[1-9]$")] | None = None
    hazmatPoisonous: Literal[0, 1] | None = None
    hazmatConcat: str | None = None
    hazmatPhone: str | None = None


class KakasQuoteRequest(BaseModel):
    quoteType: Literal[1, 2]
    pickupDate: date
    iu: Literal[0, 1]
    carType: int | None = None
    originalMsg: KakasAddress
    destinationMsg: KakasAddress
    commodityList: Annotated[list[KakasCommodity], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_ftl_car_type(self):
        if self.quoteType == 2 and self.carType is None:
            raise ValueError("carType is required when quoteType=2 (FTL)")
        return self
