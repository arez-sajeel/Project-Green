from fastapi import APIRouter
from schemas.property import PropertyBase, PropertyResponse
from controllers.property_controller import add_property_controller

router = APIRouter()

@router.post("/add", response_model=PropertyResponse)
async def add_property(property_data: PropertyBase):
    return add_property_controller(property_data.dict())
