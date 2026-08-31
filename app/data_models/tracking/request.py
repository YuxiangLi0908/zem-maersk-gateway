from pydantic import BaseModel

from app.api.common.carriers import Carrier


class TrackingRequest(BaseModel):
    carrier: Carrier = Carrier.MAERSK
    pro_number: str
