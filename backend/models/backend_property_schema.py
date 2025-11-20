from pydantic import BaseModel

class PropertyUpdate(BaseModel):
    address: str | None = None
    location: str | None = None
    sq_footage: int | None = None
    tariff_id: int | None = None
    portfolio_id: int | None = None
    mpan_id: str | None = None

    class Config:
        orm_mode = True
