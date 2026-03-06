from pydantic import BaseModel


class TrackingRequest(BaseModel):
    pro_number: str
