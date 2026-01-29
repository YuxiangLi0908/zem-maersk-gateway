from typing import Optional

from pydantic import BaseModel


class ShipperConsignee(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: str
    country: Optional[str] = None
    hotel: Optional[str] = None
    inside: Optional[str] = None
    liftgate: Optional[str] = None
    privateres: Optional[str] = None
