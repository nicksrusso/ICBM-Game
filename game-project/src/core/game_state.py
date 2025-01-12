"""
This file implements the core ICBM warfare game using Google's OpenSpiel framework.
OpenSpiel is used to enable AI agents to learn and play the game through reinforcement learning.
"""

import pyspiel
from typing import Dict, List, Tuple
from .asset import Asset


class ICBMGame(pyspiel.Game):
    """
    Main game class that defines the rules and parameters of the ICBM warfare game.
    Inherits from OpenSpiel's Game class to make it compatible with AI learning algorithms.
    """

    def __init__(self, params=None):
        # Set up basic game parameters that OpenSpiel needs to know
        game_info = pyspiel.GameInfo(
            num_distinct_actions=10000,  # Total number of different moves a player can make
            max_chance_outcomes=0,  # This is not a game of chance (like dice rolls)
            num_players=2,  # Two-player game
            min_utility=-1.0,  # Minimum score a player can get (losing)
            max_utility=1.0,  # Maximum score a player can get (winning)
            utility_sum=0.0,  # Sum of all players' scores (zero-sum game)
            max_game_length=100,  # Maximum number of turns before game ends
        )
        # Initialize the parent OpenSpiel Game class
        super().__init__(game_info, params or dict())

    def new_initial_state(self):
        """Create and return a fresh game state at the start of a new game"""
        return ICBMState(self)


class ICBMState(pyspiel.State):
    """
    Represents the current state of the game at any point during play.
    Tracks the game board, current player, and implements game rules.
    """

    def __init__(self, game):
        # Initialize the parent OpenSpiel State class
        super().__init__(game)
        self.board: Dict[Tuple[int, int], List[Asset]] = {}  # Dictionary to store game board and pieces
        self.current_player = 0  # Track whose turn it is (0 or 1)

    def current_player(self) -> int:
        """Return which player's turn it is (0 or 1)"""
        return self.current_player

    def legal_actions(self, player=None) -> List[int]:
        """
        Returns a list of all valid moves the current player can make.
        Each move is represented by a unique number (action ID).
        """
        pass

    def apply_action(self, action: int):
        """
        Execute a player's move on the game board.
        The action parameter is a number representing the chosen move.
        """
        pass

    def is_terminal(self) -> bool:
        """
        Check if the game has ended.
        Returns True if someone has won or the game is a draw.
        """
