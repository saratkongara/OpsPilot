from pydantic import BaseModel
from typing import List, Optional
from opspilot.models.enums import LocationType

class Location(BaseModel):
    id: int
    name: str
    location_type: LocationType
    parent: Optional['Location'] = None   # Reference to parent (optional)
    children: List['Location'] = []       # Sub-locations (e.g., gates within a zone)
    
    def add_child(self, location: 'Location') -> None:
        """Add a sub-location to this location."""
        self.children.append(location)
    
    def remove_child(self, location: 'Location') -> None:
        """Remove a sub-location from this location."""
        self.children.remove(location)

    def get_all_sub_locations(self) -> List['Location']:
        """Recursively fetch all sub-locations (children)."""
        sub_locations = self.children[:]
        for child in self.children:
            sub_locations.extend(child.get_all_sub_locations())
        return sub_locations

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, type={self.location_type})>"
