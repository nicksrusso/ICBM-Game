from enum import Enum
import pyspiel
from typing import Optional, List, Tuple

from icbm_game import ICBMGame
from asset import AssetType
import random


class GamePhase(Enum):
    DEPLOYMENT = "DEPLOYMENT"
    BATTLE = "BATTLE"


class ICBMGameDriver:
    def __init__(self):
        self.game = pyspiel.load_game("icbm_game")
        self.state = self.game.new_initial_state()
        self.current_phase = GamePhase.DEPLOYMENT

    def run_deployment_phase(self) -> bool:
        """Run the deployment phase until complete"""
        while not self._is_deployment_complete():
            # Get current player's legal actions
            legal_actions = self.state._legal_actions(self.state._current_player)

            if not legal_actions:
                # No legal moves available
                if not self.state.is_deployment_done(self.state._current_player):
                    return False  # Current player can't complete deployment
                self.state.switch_player()
                continue

            # Here we would interface with UI/API to get player's action
            chosen_action = self._get_player_action(legal_actions)

            # Apply the action
            self.state.apply_action(chosen_action)

            # Check if current player is done deploying
            if self.state.is_deployment_done(self.state._current_player):
                self.state.switch_player()

        # Both players have completed deployment
        return True

    def _is_deployment_complete(self) -> bool:
        """Check if both players have completed deployment"""
        return self.state.is_deployment_done(0) and self.state.is_deployment_done(1)

    def run_execution_phase(self) -> None:
        """Run a single turn of the execution phase"""
        # Build a list of all legal actions
        legal_actions = self.state._legal_actions(self.state._current_player)

        # Choose an action
        actions = self._get_player_action(legal_actions)

        # Apply action. Move asset, resolve combat, reveal any hostile assets.
        self.state.execute_turn_movements(actions)

        # Switch to next player
        self.state.switch_player()

    def _reveal_visible_enemy_assets(self) -> None:
        """Reveal any enemy assets that are visible to each player"""
        if self.state.game_phase != "DEPLOYMENT":
            # For each recorded movement
            for policy_type, action_id in self._policies_this_turn:
                # Get the asset that moved
                asset_idx, new_pos = self.decode_movement(action_id)
                moved_assets = [a for a in self._deployed_assets[self._current_player] if a.definition.is_mobile]
                if asset_idx >= len(moved_assets):
                    continue

                moved_asset = moved_assets[asset_idx]
                enemy_player = 1 - self._current_player

                # Check if moved asset is now visible to any enemy static scouts
                for enemy_asset in self._deployed_assets[enemy_player]:
                    # Only check static scout assets (radars)
                    if enemy_asset.definition.type not in (AssetType.LONG_RANGE_RADAR, AssetType.SHORT_RANGE_RADAR):
                        continue

                    # Get positions
                    moved_x, moved_y = new_pos
                    enemy_x, enemy_y = enemy_asset.position

                    # Calculate manhattan distance
                    distance = abs(enemy_x - moved_x) + abs(enemy_y - moved_y)

                    # If we moved into radar range, we're visible
                    if distance <= enemy_asset.definition.visibility_range:
                        self._visible_assets[enemy_player].add(moved_asset)
            return

        # Start with player 0
        if self.state._current_player == 1:
            self.state.switch_player()

        # Clear all visibility data
        self.state._visible_assets[0].clear()
        self.state._visible_assets[1].clear()

        # Process for first player (0), then second player (1)
        for _ in range(2):
            current_player = self.state._current_player
            enemy_player = 1 - current_player  # If current is 0, enemy is 1 and vice versa

            # Get current player's static scouting assets
            scout_assets = [
                asset
                for asset in self.state._deployed_assets[current_player]
                if asset.definition.type in (AssetType.LONG_RANGE_RADAR, AssetType.SHORT_RANGE_RADAR)
            ]

            # Check what each scout can see
            for scout in scout_assets:
                scout_x, scout_y = scout.position
                visibility_range = scout.definition.visibility_range

                # Check against all enemy assets
                for enemy_asset in self.state._deployed_assets[enemy_player]:
                    if not enemy_asset.position:
                        continue

                    enemy_x, enemy_y = enemy_asset.position
                    distance = abs(enemy_x - scout_x) + abs(enemy_y - scout_y)

                    if distance <= visibility_range:
                        self.state._visible_assets[current_player].add(enemy_asset)

            # Switch to other player for next iteration
            self.state.switch_player()

        # Reset back to player 0 after we're done
        if self.state._current_player == 1:
            self.state.switch_player()

        return True

    def _get_player_action(self, legal_actions: List[int]) -> List[int]:
        """Temporary placeholder for getting player input"""
        # This would be replaced by actual UI/API integration

        if self.state.game_phase == "DEPLOYMENT":
            if not self.state._has_citadel[self.state._current_player]:
                return legal_actions[0]  # Just take first legal action for now
            else:
                return legal_actions[random.randint(0, len(legal_actions) - 1)]
        else:
            return [legal_actions[0]]  # Just take first legal action for now


def main():
    driver = ICBMGameDriver()

    # Run deployment phase
    if not driver.run_deployment_phase():
        print("Deployment phase failed")
        return

    print("Deployment complete, starting game phase")

    driver.state.game_phase = "BATTLE"

    driver._reveal_visible_enemy_assets()

    # Run game until victory condition met
    while True:
        driver.run_execution_phase()

        # Check victory conditions
        if driver.state._victory_points[0] <= 0:
            print("Player 2 wins!")
            break
        elif driver.state._victory_points[1] <= 0:
            print("Player 1 wins!")
            break


if __name__ == "__main__":
    main()
