from typing import List, Optional

from pydantic import BaseModel

from app.data_models.rating.line_item import LineItem
from app.data_models.rating.shipper_consignee import ShipperConsignee


class RatingRequest(BaseModel):
    shipDate: str
    origin_zip: str
    dest_zip: str
    lineItems: List[LineItem]
    declaredValue: Optional[str] = None
    insuranceValue: Optional[str] = None
    debrisRemoval: Optional[str] = None
