import numpy as np
from typing import List, Dict, Optional, Tuple

import pyspiel
from icbm_game.asset import AssetType, Asset, load_asset_definitions
from dataclasses import dataclass

_NUM_PLAYERS = 2
_NUM_ROWS = 10
_NUM_COLS = 20
_STARTING_POINTS = 125
_VICTORY_POINTS = 100


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

        # Decode action
        if action_id < len(AssetType):  # Purchase action
            # Convert index to AssetType
            asset_type = list(AssetType)[action_id]
            self.purchase_asset(self._current_player, asset_type)
        else:  # Deploy action
            action_id -= len(AssetType)
            asset_idx = action_id // (_NUM_ROWS * (_NUM_COLS // 2))
            pos_id = action_id % (_NUM_ROWS * (_NUM_COLS // 2))
            row = pos_id // (_NUM_COLS // 2)
            col = pos_id % (_NUM_COLS // 2)
            if self._current_player == 1:
                col += _NUM_COLS // 2
            self.deploy_asset(self._current_player, asset_idx, (row, col))

    def deploy_asset(self, player: int, asset_idx: int, position: Tuple[int, int]) -> bool:
        """Attempt to deploy a purchased asset"""
        if asset_idx >= len(self._purchased_assets[player]):
            return False

        asset = self._purchased_assets[player][asset_idx]
        if not self.can_deploy(player, asset, position):
            return False

        # Update asset position and move to deployed list
        asset.position = position
        self._deployed_assets[player].append(asset)
        self._purchased_assets[player].pop(asset_idx)

        # Track citadel deployment
        if asset.definition.type == AssetType.CITADEL:
            self._has_citadel[player] = True

        return True

    def is_deployment_done(self, player: int) -> bool:
        """Check if player has finished deployment"""
        return self._has_citadel[player] and len(self._purchased_assets[player]) == 0

    def _legal_actions(self, player: int) -> List[int]:
        """Returns a list of legal actions."""
        if self.game_phase != "DEPLOYMENT":
            return []  # TODO: Implement game phase actions

        actions = []
        action_id = 0

        # Allow purchases if points available
        for asset_type in AssetType:
            if self.can_purchase(player, asset_type):
                actions.append(action_id)
            action_id += 1

        # Allow deployments of purchased assets
        rows, cols = self.get_player_area(player)
        for asset_idx in range(len(self._purchased_assets[player])):
            for row in range(rows.start, rows.stop):
                for col in range(cols.start, cols.stop):
                    if self.can_deploy(player, self._purchased_assets[player][asset_idx], (row, col)):
                        actions.append(action_id)
                    action_id += 1

        return actions


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
