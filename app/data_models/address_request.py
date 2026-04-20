from pydantic import BaseModel

class AddressRequest(BaseModel):
    street: str
    city: str
    state: str
    zipcode: str
    country: str