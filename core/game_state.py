from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np


@dataclass
class Player:
    victory_points: int = 100
    game_phase: str='DEPLOY'
    assets: Dict[str, List[Tuple[int, int]]] = None  # Maps asset_id to positions
    visible_enemies: Dict[str, Tuple[int, int]] = None  # Currently visible enemy assets
    

    def __post_init__(self):
        if self.assets is None:
            self.assets = {}
        if self.visible_enemies is None:
            self.visible_enemies = {}


class GameState:
    def __init__(self, board_size: Tuple[int, int] = (20, 10), num_players: int = 2):
        self.board_size = board_size
        self.turn_count = 0
        self.current_player = 0  # 0 for red, 1 for blue
        self.players = [Player(), Player()]
        self.points_per_turn = 5
        self.game_over = False

    def apply_turn_penalty(self):
        """Apply the 5 point penalty for taking a turn"""
        self.players[self.current_player].victory_points -= self.points_per_turn
        self._check_victory_conditions()

    def switch_turn(self):
        """Switch to the other player's turn"""
        self.current_player = 1 - self.current_player
        self.turn_count += 1

    def _check_victory_conditions(self):
        """Check if either player has reached 0 victory points"""
        for player in self.players:
            if player.victory_points <= 0:
                self.game_over = True
                return True
        return False

    def get_player_state(self, player_id: int) -> Player
        """Get the state for a specific player"""
        return self.players[player_id]

    def destroy_citadel(self, player_id: int):
        """Handle citadel destruction"""
        self.players[player_id].victory_points -= 100
        self._check_victory_conditions()
