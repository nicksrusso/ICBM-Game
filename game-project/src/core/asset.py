from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AssetDefinition:
    """Static definition of an asset type"""

    name: str
    type: str
    visibility_range: int
    cost: int
    is_mobile: bool
    speed: int
    range: int


class Asset:
    """Instance of an asset in the game"""

    def __init__(self, definition: AssetDefinition, position: Tuple[int, int], owner: int):
        self.definition = definition  # Immutable properties
        self.id = id(self)  # Unique ID for hashing

        # Mutable state
        self.position = position
        self.owner = owner
        self.is_active = False  # For assets that need launching
        self.is_destroyed = False  # Track if asset is destroyed
        self.has_moved_this_turn = False  # Track movement
        self.has_acted_this_turn = False  # Track actions (attacking, scouting)
        self.last_known_position = position  # For tracking through fog of war
        self.visible_to = None  # Players that can see this asset

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, Asset):
            return False
        return self.id == other.id

    def move_to(self, new_position: Tuple[int, int]):
        """Move asset to new position"""
        self.position = new_position
        self.has_moved_this_turn = True

    def launch(self):
        """Launch a mobile asset"""
        if self.definition.is_mobile:
            self.is_active = True

    def reset_turn_state(self):
        """Reset per-turn state"""
        self.has_moved_this_turn = False
        self.has_acted_this_turn = False
