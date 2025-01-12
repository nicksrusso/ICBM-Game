import numpy as np
from typing import List, Dict, Optional, Tuple

import pyspiel
from asset import AssetType, Asset, load_asset_definitions
from dataclasses import dataclass
from enum import Enum

_NUM_PLAYERS = 2
_NUM_ROWS = 10
_NUM_COLS = 20
_STARTING_POINTS = 125
_VICTORY_POINTS = 100


class GamePhase(Enum):
    DEPLOYMENT = "DEPLOYMENT"
    EXECUTION = "EXECUTION"
    MOVEMENT = "MOVEMENT"
    COMBAT = "COMBAT"
    SCOUTING = "SCOUTING"


class ICBMGame(pyspiel.Game):
    """A two-player zero-sum game representing ICBM warfare."""

    def __init__(self, params=None):
        """Initialize the game."""

        game_info = pyspiel.GameInfo(
            num_distinct_actions=_NUM_ROWS * _NUM_COLS + 1,  # +1 for pass action
            max_chance_outcomes=0,
            num_players=_NUM_PLAYERS,
            min_utility=-1.0,  # Loss
            max_utility=1.0,  # Win
            utility_sum=0.0,  # Zero-sum game
            max_game_length=1000,
        )
        super().__init__(_GAME_TYPE, game_info, params or {})

    def new_initial_state(self):
        """Returns a new ICBMState."""
        return ICBMState(self)

    def max_chance_outcomes(self):
        """Returns the maximum number of chance outcomes."""
        return 0

    def num_distinct_actions(self):
        """Returns the number of possible actions."""
        # TODO: Calculate total number of possible actions
        return _NUM_ROWS * _NUM_COLS + 1  # +1 for pass action

    def max_game_length(self):
        """Returns the maximum length of a game."""
        return 1000  # Set a reasonable maximum

    def num_players(self):
        """Returns the number of players."""
        return _NUM_PLAYERS


@dataclass
class DeploymentAction:
    """Represents a deployment action"""

    action_type: str  # "purchase" or "deploy"
    asset_type: Optional[AssetType] = None
    position: Optional[Tuple[int, int]] = None


class ICBMState(pyspiel.State):
    """State of the game."""

    def __init__(self, game):
        super().__init__(game)
        self.game_phase = "DEPLOYMENT"
        self._current_player = 0
        self._players_points = [_STARTING_POINTS, _STARTING_POINTS]
        self._victory_points = [_VICTORY_POINTS, _VICTORY_POINTS]

        # Deployment phase tracking
        self._purchased_assets = {0: [], 1: []}  # Assets bought but not deployed
        self._deployed_assets = {0: [], 1: []}  # Assets on the board
        self._has_citadel = {0: False, 1: False}  # Track if citadel deployed
        self.assets = load_asset_definitions()

        # Board representation
        self._board = np.zeros((_NUM_ROWS, _NUM_COLS), dtype=int)

        # Visibility tracking
        self._visible_assets = {0: set(), 1: set()}  # Assets visible to each player

        # Turn tracking
        self._turn_number = 0
        self._policies_this_turn = []  # List of moves to resolve

        # Movement tracking
        self._pending_movements = {}  # Asset -> target_position

        # Combat results
        self._destroyed_assets = set()

    def get_player_area(self, player: int) -> Tuple[slice, slice]:
        """Get the valid deployment area for a player"""
        if player == 0:
            return (slice(0, _NUM_ROWS), slice(0, _NUM_COLS // 2))
        return (slice(0, _NUM_ROWS), slice(_NUM_COLS // 2, _NUM_COLS))

    # Add the new method here
    def switch_player(self) -> None:
        """Switch to the other player's turn."""
        self._current_player = 1 - self._current_player  # Alternates between 0 and 1

    def can_purchase(self, player: int, asset_type: AssetType) -> bool:
        """Check if player can purchase the given asset"""
        asset_def = self.assets[asset_type]
        return self._players_points[player] >= asset_def.cost

    def purchase_asset(self, player: int, asset_type: AssetType) -> bool:
        """Attempt to purchase an asset"""
        if not self.can_purchase(player, asset_type):
            return False

        asset_def = self.assets[asset_type]
        self._players_points[player] -= asset_def.cost
        self._purchased_assets[player].append(Asset(definition=asset_def, player=player))
        return True

    def can_deploy(self, player: int, asset: Asset, position: Tuple[int, int]) -> bool:
        """Check if asset can be deployed to position"""
        row, col = position
        player_area = self.get_player_area(player)

        # Check if position is in player's area
        if not (player_area[0].start <= row < player_area[0].stop and player_area[1].start <= col < player_area[1].stop):
            return False

        # Static assets can't be co-located
        if not asset.definition.is_mobile:
            for deployed in self._deployed_assets[player]:
                if not deployed.definition.is_mobile:
                    d_row, d_col = deployed.position
                    if d_row == row and d_col == col:
                        return False

        # Mobile assets must be deployed to launch sites
        if asset.definition.is_mobile:
            has_launch_site = False
            for deployed in self._deployed_assets[player]:
                if deployed.definition.type == AssetType.LAUNCH_SITE and deployed.position == position:
                    has_launch_site = True
                    break
            if not has_launch_site:
                return False

        return True

    def apply_action(self, action_id: int) -> None:
        """Apply specified action."""
        if self.game_phase != "DEPLOYMENT":
            return  # TODO: Implement game phase actions

        # Get player's area
        player_area = self.get_player_area(self._current_player)
        rows = range(player_area[0].start, player_area[0].stop)
        cols = range(player_area[1].start, player_area[1].stop)
        positions_per_asset = len(rows) * len(cols)

        # First, build list of purchasable assets in order
        has_launch_site = any(
            asset.definition.type == AssetType.LAUNCH_SITE for asset in self._deployed_assets[self._current_player]
        )

        purchasable_assets = []
        for asset_type in AssetType:
            asset_def = self.assets[asset_type]
            if asset_type == AssetType.CITADEL and self._has_citadel[self._current_player]:
                continue
            if asset_def.is_mobile and not has_launch_site and asset_type != AssetType.LAUNCH_SITE:
                continue
            if self.can_purchase(self._current_player, asset_type):
                purchasable_assets.append(asset_type)

        # Determine which asset type and position
        asset_type_idx = action_id // positions_per_asset
        position_idx = action_id % positions_per_asset

        if asset_type_idx >= len(purchasable_assets):
            return  # Invalid action

        # Convert to actual position
        row = rows.start + (position_idx // len(cols))
        col = cols.start + (position_idx % len(cols))

        # Get the actual purchasable asset type
        asset_type = purchasable_assets[asset_type_idx]

        # Purchase and deploy
        if self.purchase_asset(self._current_player, asset_type):
            self.deploy_asset(self._current_player, -1, (row, col))

    def deploy_asset(self, player: int, asset_idx: int, position: Tuple[int, int]) -> bool:
        """Deploy a purchased asset to the board

        Args:
            player: Player ID (0 or 1)
            asset_idx: Index of asset in purchased assets list
            position: (row, col) position to deploy to
        """
        if asset_idx >= len(self._purchased_assets[player]):
            return False

        asset = self._purchased_assets[player][asset_idx]
        if not self.can_deploy(player, asset, position):
            return False

        # Update asset position and move to deployed list
        asset.position = position
        self._deployed_assets[player].append(asset)
        self._purchased_assets[player].pop(asset_idx)

        # Only add static assets to the board representation
        if not asset.definition.is_mobile:
            row, col = position
            # Encode as: player_id * 100 + asset_type_id
            asset_type_id = list(AssetType).index(asset.definition.type) + 1
            self._board[row, col] = player * 100 + asset_type_id

        # Track citadel deployment
        if asset.definition.type == AssetType.CITADEL:
            self._has_citadel[player] = True

        return True

    def get_static_asset_at_position(self, position: Tuple[int, int]) -> Optional[Tuple[int, AssetType]]:
        """Get the player ID and asset type of static asset at a position

        Returns:
            Tuple of (player_id, AssetType) or None if empty
        """
        row, col = position
        board_val = self._board[row, col]
        if board_val == 0:
            return None

        player = board_val // 100
        asset_type_id = (board_val % 100) - 1
        return (player, list(AssetType)[asset_type_id])

    def get_assets_at_position(self, position: Tuple[int, int]) -> List[Asset]:
        """Get all assets (static and mobile) at a position"""
        assets = []
        for player in range(_NUM_PLAYERS):
            for asset in self._deployed_assets[player]:
                if asset.position == position:
                    assets.append(asset)
        return assets

    def is_deployment_done(self, player: int) -> bool:
        """Check if player has finished deployment"""
        return self._has_citadel[player] and len(self._purchased_assets[player]) == 0 and self._players_points[player] == 0

    def _legal_actions(self, player: int) -> List[int]:
        """Returns a list of legal actions."""
        if self.game_phase != "DEPLOYMENT":
            actions = []
            # Get all mobile assets for this player
            mobile_assets = [
                asset for asset in self._deployed_assets[player] if asset.definition.is_mobile and not asset.is_destroyed
            ]

            # For each mobile asset, find all possible moves within its speed range
            for asset_idx, asset in enumerate(mobile_assets):
                if not asset.position:  # Skip if asset has no position
                    continue

                current_x, current_y = asset.position
                speed = asset.definition.speed

                # Check all positions within manhattan distance of speed
                for dx in range(-speed, speed + 1):
                    for dy in range(-speed - abs(dx), speed - abs(dx) + 1):
                        new_x = current_x + dx
                        new_y = current_y + dy

                        # Check if position is on board
                        if 0 <= new_x < _NUM_ROWS and 0 <= new_y < _NUM_COLS:
                            # Convert to action ID:
                            # action_id = asset_index * (total_board_positions) + position_index
                            position_index = new_x * _NUM_COLS + new_y
                            action_id = asset_idx * (_NUM_ROWS * _NUM_COLS) + position_index
                            actions.append(action_id)

            return actions

        actions = []
        action_id = 0
        player_area = self.get_player_area(player)
        rows = range(player_area[0].start, player_area[0].stop)
        cols = range(player_area[1].start, player_area[1].stop)

        # Check if player has a launch site so we can prevent purchase of mobile assets unil we have a place to deploy them
        has_launch_site = any(asset.definition.type == AssetType.LAUNCH_SITE for asset in self._deployed_assets[player])

        # Check deployments for each purchasable asset type
        for asset_type in AssetType:
            asset_def = self.assets[asset_type]

            # Skip citadel if player already has one
            if asset_type == AssetType.CITADEL and self._has_citadel[player]:
                continue

            # Skip mobile assets if no launch site (except the launch site itself)
            if asset_def.is_mobile and not has_launch_site and asset_type != AssetType.LAUNCH_SITE:
                continue

            if self.can_purchase(player, asset_type):
                # Create temporary asset for position checking
                temp_asset = Asset(definition=self.assets[asset_type], player=player)

                # Check each possible position
                # TODO: For efficiency, only check positions of launch sites for mobile assets
                for row in range(rows.start, rows.stop):
                    for col in range(cols.start, cols.stop):
                        if self.can_deploy(player, temp_asset, (row, col)):
                            actions.append(action_id)
                        action_id += 1

        return actions

    def decode_action(self, action_id: int) -> Tuple[int, Tuple[int, int]]:
        """Convert action_id back into asset_index and target position. Used for decoding actions in the game phase, not deployment phase"""
        total_positions = _NUM_ROWS * _NUM_COLS
        asset_idx = action_id // total_positions
        position_id = action_id % total_positions
        target_x = position_id // _NUM_COLS
        target_y = position_id % _NUM_COLS
        return asset_idx, (target_x, target_y)

    # def apply_policies(self, policies: List[Policy]) -> None:
    # """Queue up policies (moves) for the current turn"""

    def execute_turn(self) -> None:
        """Process through EXECUTION -> MOVEMENT -> COMBAT -> SCOUTING phases"""

    def update_visibility(self) -> None:
        """Update what assets each player can see based on scouting assets"""

    def resolve_combat(self) -> None:
        """Handle combat between assets that end up on same tile"""

    def calculate_victory_points(self) -> None:
        """Update victory points based on turn actions and destroyed assets"""

    def get_visible_state(self, player: int) -> Dict:
        """Return the game state as visible to the given player"""


# Define game type
_GAME_TYPE = pyspiel.GameType(
    short_name="icbm_game",
    long_name="ICBM Warfare Game",
    dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
    chance_mode=pyspiel.GameType.ChanceMode.DETERMINISTIC,
    information=pyspiel.GameType.Information.IMPERFECT_INFORMATION,
    utility=pyspiel.GameType.Utility.ZERO_SUM,
    reward_model=pyspiel.GameType.RewardModel.TERMINAL,
    max_num_players=_NUM_PLAYERS,
    min_num_players=_NUM_PLAYERS,
    provides_information_state_string=True,
    provides_information_state_tensor=True,
    provides_observation_string=True,
    provides_observation_tensor=True,
    parameter_specification={},
)

# Game registration
pyspiel.register_game(_GAME_TYPE, ICBMGame)
