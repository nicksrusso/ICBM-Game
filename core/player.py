from asset import Asset


class Player:
    def __init__(self, ID: str, territory: list[list], victory_points: int, cash: int):
        self.ID = ID
        self.territory = territory
        self.victory_points = victory_points
        self.cash = cash
        self.assets = None

        self.visible_hostile_assets = None

    def deploy_assets():
        pass

    def enumerate_possible_moves():
        pass
