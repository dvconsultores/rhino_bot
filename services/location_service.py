# services/location_service.py
from models.locations import Locations
from db import db

def get_all_locations():
    """Retrieve all locations."""
    return Locations.query.all()

def get_location_by_id(location_id):
    """Retrieve a location by its ID."""
    return Locations.query.get(location_id)

def create_location(data):
    """Create a new location."""
    new_location = Locations(
        location=data.get('location'),
        address=data.get('address')
    )
    db.session.add(new_location)
    db.session.commit()
    return new_location

def update_location(location_id, data):
    """Update an existing location."""
    location = Locations.query.get(location_id)
    if not location:
        return None

    location.location = data.get('location', location.location)
    location.address = data.get('address', location.address)
    db.session.commit()
    return location

def delete_location(location_id):
    """Delete a location."""
    location = Locations.query.get(location_id)
    if not location:
        return None

    db.session.delete(location)
    db.session.commit()
    return location
