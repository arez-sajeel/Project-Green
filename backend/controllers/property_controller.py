from config.database import property_collection
from fastapi import HTTPException

def add_property_controller(data):
    result = property_collection.insert_one(data)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Could not save property")

    return { "id": str(result.inserted_id), **data }
