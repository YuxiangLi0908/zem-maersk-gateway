from typing import List, Optional

from pydantic import BaseModel

from app.api.common.carriers import Carrier
from app.data_models.rating.line_item import LineItem


class RatingRequest(BaseModel):
    carrier: Carrier = Carrier.MAERSK
    shipDate: str
    origin_zip: str
    dest_zip: str
    lineItems: List[LineItem]
    liftgate: Optional[str] = None
    declaredValue: Optional[str] = None
    insuranceValue: Optional[str] = None
    debrisRemoval: Optional[str] = None
