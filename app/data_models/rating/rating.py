from typing import List, Optional

from pydantic import BaseModel

from app.data_models.rating.line_item import LineItem
from app.data_models.rating.shipper_consignee import ShipperConsignee


class Rating(BaseModel):
    shipper: ShipperConsignee
    consignee: ShipperConsignee
    lineItems: List[LineItem]
    locationID: str
    tariffHeaderID: str
    shipDate: str
    declaredValue: Optional[str] = None
    insuranceValue: Optional[str] = None
    debrisRemoval: Optional[str] = None
