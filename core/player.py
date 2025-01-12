from asset import Asset

from typing import Dict, Optional, List, Tuple


class Player:
    def __init__(self, ID: str, territory: list[list], victory_points: int, cash: int):
        self.ID = ID
        self.territory = territory
        self.victory_points = victory_points
        self.cash = cash
        self.assets = None

        self.visible_hostile_assets = None
        self.board: Dict[Tuple[int, int], List[Asset]] = {}

    def set_board_reference(self, board: Dict[Tuple[int, int], List[Asset]]):
        """Set reference to the shared game board"""
        self.board_ref = board

    def deploy_assets():

        pass

    def enumerate_possible_moves():
        pass
