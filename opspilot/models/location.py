from pydantic import BaseModel
from typing import List, Dict, Optional

class Location(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
        
    def get_children(self, location_map: Dict[int, 'Location']) -> List['Location']:
        """Get immediate children of this location using a location ID map."""
        return [loc for loc in location_map.values() if loc.parent_id == self.id]
    
    def get_all_descendants(self, location_map: Dict[int, 'Location']) -> List['Location']:
        """Recursively fetch all sub-locations (children, grandchildren, etc.)."""
        descendants = []
        for child in self.get_children(location_map):
            descendants.append(child)
            descendants.extend(child.get_all_descendants(location_map))
        return descendants
    
    def get_parent(self, location_map: Dict[int, 'Location']) -> Optional['Location']:
        """Get parent location if it exists."""
        return location_map.get(self.parent_id) if self.parent_id else None
    
    def add_child(self, child: 'Location') -> None:
        """Establish parent-child relationship (one-way)."""
        child.parent_id = self.id
    
    def remove_child(self, child: 'Location') -> None:
        """Remove parent-child relationship."""
        if child.parent_id == self.id:
            child.parent_id = None
    
    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, parent_id={self.parent_id})>"