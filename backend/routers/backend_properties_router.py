from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.data_access.database import get_db
from backend.models.property import Property
from backend.schemas.property_schema import PropertyUpdate
from backend.core.security import get_current_user

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("/{property_id}")
def get_property(property_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop

@router.patch("/{property_id}")
def update_property(property_id: int, update_data: PropertyUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    update_values = update_data.dict(exclude_unset=True)
    for field, value in update_values.items():
        setattr(prop, field, value)

    db.commit()
    db.refresh(prop)
    return prop
