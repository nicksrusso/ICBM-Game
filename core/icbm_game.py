from typing import Dict, Optional, List, Set, Tuple
import pandas as pd
import numpy as np
import io
from asset import AssetDefinition, Asset
import json
from player import Player


class ICBMGame:
    """Main game class implementing the ICBM warfare game"""

    def __init__(self, asset_config_path: str, game_config_path: str):

        # Load asset definitions
        self.asset_defs = self._load_asset_definitions(asset_config_path)

        # Load game config
        with open(game_config_path, "r") as f:
            game_conf = json.load(f)
        self.board_size = game_conf["board_size"]

        # Initialize the list of desired players
        self.players = []
        for player in game_conf["players"]:
            self.players.append(
                Player(
                    ID=player["ID"],
                    territory=player["TERRITORY"],
                    victory_points=player["VICTORYPOINTS"],
                    cash=player["STARTINGCASH"],
                )
            )

        # Set index for whose turn it is to 0
        self.current_player = 0
        self.game_phase = "DEPLOYMENT"

        # Create a null board
        self.board: Dict[Tuple[int, int], List[Asset]] = {}

        # Game state
        # self.reset_game()

    def _get_asset_config_path(self) -> str:
        """Determine the path to asset definitions file"""
        import os
        import pathlib

        # Check environment variable first
        env_path = os.environ.get("ASSET_DEF")
        if env_path:
            if not os.path.exists(env_path):
                raise FileNotFoundError(f"Asset definition file specified in ASSET_DEF not found: {env_path}")
            return env_path

        # If no environment variable, construct default path
        current_file = pathlib.Path(__file__)
        default_path = current_file.parent.parent / "game_rules" / "asset_definitions.csv"

        if not default_path.exists():
            raise FileNotFoundError(f"Default asset definition file not found at: {default_path}")

        return str(default_path)

    def _load_asset_definitions(self, config_path: str) -> Dict[str, AssetDefinition]:
        """Load asset definitions from CSV file"""
        with open(config_path, "r") as f:
            df = pd.read_csv(f)

        assets = {}
        for _, row in df.iterrows():
            asset_def = AssetDefinition(
                name=row["Name"],
                type=row["Type"],
                visibility_range=row["VisibilityRange"],
                cost=row["Cost"],
                is_mobile=row["IsMobile"],
                speed=row["Speed"],
                range=row["Range"],
            )
            assets[asset_def.name] = asset_def

        return assets

    def reset_game(self):
        """Reset the game to initial state"""
        # Player resources
        self.points = [self.STARTING_POINTS, self.STARTING_POINTS]
        self.victory_points = [self.STARTING_VICTORY_POINTS, self.STARTING_VICTORY_POINTS]

        # Game phase (0=deployment, 1=play)
        self.phase = 0

        # Current player (0 or 1)
        self.current_player = 0

        # Game board - dictionary mapping (x,y) to list of assets at that position
        self.board: Dict[Tuple[int, int], List[Asset]] = {}

        # Track assets by player
        self.player_assets: List[Set[Asset]] = [set(), set()]

        # Track visible assets
        self.visible_assets: Set[Asset] = set()

        # Track number of turns
        self.turn_number = 0

    def is_valid_deploy_position(self, x: int, y: int, player: int) -> bool:
        """Check if position is valid for deployment for given player"""
        if not (0 <= x < self.BOARD_WIDTH):
            return False

        # Player 0 deploys in bottom half, Player 1 in top half
        if player == 0:
            return 0 <= y < self.BOARD_HEIGHT // 2
        else:
            return self.BOARD_HEIGHT // 2 <= y < self.BOARD_HEIGHT

    def deploy_asset(self, asset_name: str, x: int, y: int) -> bool:
        """Attempt to deploy an asset. Returns success boolean."""
        # Verify we're in deployment phase
        if self.phase != 0:
            return False

        # Get asset definition
        asset_def = self.asset_defs.get(asset_name)
        if not asset_def:
            return False

        # Check if player has enough points
        if self.points[self.current_player] < asset_def.cost:
            return False

        # Validate position
        if not self.is_valid_deploy_position(x, y, self.current_player):
            return False

        pos = (x, y)

        # Handle static asset co-location restriction
        if not asset_def.is_mobile:
            # Check if any static assets already at this position
            if pos in self.board:
                for existing_asset in self.board[pos]:
                    if not existing_asset.definition.is_mobile:
                        return False

        # Handle launch site requirement for mobile assets
        if asset_def.is_mobile:
            has_launch_site = False
            if pos in self.board:
                for existing_asset in self.board[pos]:
                    if existing_asset.definition.type == "base" and existing_asset.owner == self.current_player:
                        has_launch_site = True
                        break
            if not has_launch_site:
                return False

        # Create new asset instance
        new_asset = Asset(definition=asset_def, position=pos, owner=self.current_player)

        # Add to board and player assets
        if pos not in self.board:
            self.board[pos] = []
        self.board[pos].append(new_asset)

        self.players[self.current_player].add(new_asset)

        # Deduct points
        self.points[self.current_player] -= asset_def.cost

        return True

    def is_valid_deployment(self) -> bool:
        """Check if current deployment state is valid"""
        for player in [0, 1]:
            # Must have exactly one citadel
            citadel_count = sum(1 for asset in self.player_assets[player] if asset.definition.name == "CITADEL")
            if citadel_count != 1:
                return False

            # Each mobile asset must be at a launch site
            for asset in self.player_assets[player]:
                if asset.definition.is_mobile:
                    has_launch_site = False
                    for board_asset in self.board[asset.position]:
                        if board_asset.definition.type == "base" and board_asset.owner == player:
                            has_launch_site = True
                            break
                    if not has_launch_site:
                        return False

        return True

    def end_deployment_turn(self) -> bool:
        """End current player's deployment turn"""
        if self.phase != 0:
            return False

        self.current_player = 1 - self.current_player
        return True

    def get_deployable_assets(self) -> Dict[str, int]:
        """Get dictionary of asset names to number that can be afforded"""
        affordable = {}
        for name, asset_def in self.asset_defs.items():
            # Special case for citadel - free and can only deploy one if not already deployed
            if name == "CITADEL":
                citadel_count = sum(
                    1 for asset in self.player_assets[self.current_player] if asset.definition.type == "CITADEL"
                )
                if citadel_count == 0:
                    affordable[name] = 1
                continue

            # For all other assets
            if asset_def.cost > 0:  # Avoid divide by zero
                count = self.points[self.current_player] // asset_def.cost
                if count > 0:
                    affordable[name] = count

        return affordable

    def start_play_phase(self) -> bool:
        """Attempt to start play phase. Returns success boolean."""
        # Verify all players have deployed citadel
        for player_idx, assets in enumerate(self.player_assets):
            has_citadel = any(asset.definition.type == "CITADEL" for asset in assets)
            if not has_citadel:
                return False

        self.phase = 1
        return True

    def end_turn(self):
        """End current player's turn"""
        # Update victory points
        self.victory_points[self.current_player] -= self.POINTS_PER_TURN

        # Switch players
        self.current_player = 1 - self.current_player

        if self.current_player == 0:
            self.turn_number += 1

        # Update visibility
        self._update_visibility()

    def _update_visibility(self):
        """Update which assets are visible to each player"""
        self.visible_assets.clear()

        # For each scouting asset
        for player_assets in self.player_assets:
            for asset in player_assets:
                if asset.visibility_range > 0:  # Is a scouting asset
                    x, y = asset.position
                    # Check all positions within visibility range
                    for dx in range(-asset.visibility_range, asset.visibility_range + 1):
                        for dy in range(-asset.visibility_range, asset.visibility_range + 1):
                            pos = (x + dx, y + dy)
                            if pos in self.board:
                                for target in self.board[pos]:
                                    if target.owner != asset.owner:
                                        self.visible_assets.add(target)

    def get_winner(self) -> Optional[int]:
        """Get winner (0 or 1) if game is over, None otherwise"""
        # Check victory points
        for player in [0, 1]:
            if self.victory_points[player] <= 0:
                return 1 - player  # Other player wins

        # Check if either citadel is destroyed
        for player in [0, 1]:
            has_citadel = any(asset.type == "CITADEL" for asset in self.player_assets[player])
            if not has_citadel:
                return 1 - player  # Other player wins

        return None  # Game not over

    def get_valid_moves(self) -> List[Tuple[str, List[any]]]:
        """Get list of valid moves for current player"""
        # TODO: Implement move validation
        return []

    def make_move(self, move_type: str, params: List[any]) -> bool:
        """Attempt to make a move. Returns success boolean."""
        # TODO: Implement move execution
        return False
