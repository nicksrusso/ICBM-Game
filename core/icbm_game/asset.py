from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, Dict


class AssetType(Enum):
    CITADEL = "CITADEL"
    LAUNCH_SITE = "LAUNCH_SITE"
    ICBM = "ICBM"
    CRUISE_MISSILE = "CRUISE_MISSILE"
    ARTILLERY = "ARTILLERY"
    LONG_RANGE_INTERCEPTOR = "LONG_RANGE_INTERCEPTOR"
    SHORT_RANGE_INTERCEPTOR = "SHORT_RANGE_INTERCEPTOR"
    POINT_DEFENSE = "POINT_DEFENSE_INTERCEPTOR"
    SATELLITE = "SATELLITE"
    RECON_PLANE = "RECON_PLANE"
    LONG_RANGE_RADAR = "LONG_RANGE_RADAR"
    SHORT_RANGE_RADAR = "SHORT_RANGE_RADAR"


@dataclass
class AssetDefinition:
    type: AssetType
    visibility_range: int
    cost: int
    is_mobile: bool
    speed: int
    range: int


@dataclass
class Asset:
    """Represents a placed asset on the board"""

    definition: AssetDefinition
    player: int
    position: Optional[Tuple[int, int]] = None
    is_active: bool = False  # For scouting assets
    is_destroyed: bool = False

    @property
    def is_revealed(self) -> bool:
        """Whether this asset is currently visible to the opponent"""
        return False  # TODO: Implement based on scouting mechanics

    def can_move_to(self, new_pos: Tuple[int, int]) -> bool:
        """Check if asset can move to the given position"""
        if not self.definition.is_mobile:
            return False

        if self.position is None:
            return False

        x1, y1 = self.position
        x2, y2 = new_pos
        manhattan_dist = abs(x2 - x1) + abs(y2 - y1)

        return manhattan_dist <= self.definition.speed


def load_asset_definitions() -> Dict[AssetType, AssetDefinition]:
    """Load asset definitions from CSV file."""
    import csv
    from pathlib import Path

    assets = {}
    csv_path = Path(__file__).parent / "asset_definitions.csv"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset_type = AssetType(row["Name"])  # Convert name to enum
            assets[asset_type] = AssetDefinition(
                type=asset_type,
                visibility_range=int(row["VisibilityRange"]),
                cost=int(row["Cost"]),
                is_mobile=row["IsMobile"].lower() == "true",
                speed=int(row["Speed"]),
                range=int(row["Range"]),
            )
    return assets
