import unittest
import pyspiel
from icbm_game.icbm_game import (
    ICBMGame,
    AssetType,
    _NUM_ROWS,
    _NUM_COLS,
)


class TestICBMGameDeployment(unittest.TestCase):
    def setUp(self):
        self.game = pyspiel.load_game("icbm_game")
        self.state = self.game.new_initial_state()

    def test_deployment_sequence(self):
        # Verify we start in deployment phase
        self.assertEqual(self.state.game_phase, "DEPLOYMENT")
        self.assertEqual(self.state._current_player, 0)

        # Player 1 purchases
        citadel_action = list(AssetType).index(AssetType.CITADEL)
        launch_site_action = list(AssetType).index(AssetType.LAUNCH_SITE)
        icbm_action = list(AssetType).index(AssetType.ICBM)

        # Purchase assets for player 1
        self.state.apply_action(citadel_action)
        self.state.apply_action(launch_site_action)
        self.state.apply_action(icbm_action)

        # Verify purchases
        self.assertEqual(len(self.state._purchased_assets[0]), 3)

        # Deploy assets for player 1
        # Deploy citadel at (0,0)
        citadel_pos = (0, 0)
        deploy_action = len(AssetType) + (
            0 * (_NUM_ROWS * (_NUM_COLS // 2)) + citadel_pos[0] * (_NUM_COLS // 2) + citadel_pos[1]
        )
        self.state.apply_action(deploy_action)

        # Deploy launch site at (0,1)
        launch_pos = (0, 1)
        deploy_action = len(AssetType) + (
            0 * (_NUM_ROWS * (_NUM_COLS // 2)) + launch_pos[0] * (_NUM_COLS // 2) + launch_pos[1]
        )
        self.state.apply_action(deploy_action)

        # Deploy ICBM at launch site (0,1)
        deploy_action = len(AssetType) + (
            0 * (_NUM_ROWS * (_NUM_COLS // 2)) + launch_pos[0] * (_NUM_COLS // 2) + launch_pos[1]
        )
        self.state.apply_action(deploy_action)

        # Verify player 1 deployments
        self.assertEqual(len(self.state._deployed_assets[0]), 3)
        self.assertTrue(self.state._has_citadel[0])
        self.assertEqual(self.state._current_player, 0)  # Should switch to player 2

        self.state.switch_player()
        self.assertEqual(self.state._current_player, 1)

        # Player 2 purchases and deploys citadel
        self.state.apply_action(citadel_action)

        # Deploy citadel at (0,10) - first position in player 2's area
        citadel_pos = (0, 0)  # Will be offset automatically for player 2
        deploy_action = len(AssetType) + (
            0 * (_NUM_ROWS * (_NUM_COLS // 2)) + citadel_pos[0] * (_NUM_COLS // 2) + citadel_pos[1]
        )
        self.state.apply_action(deploy_action)

        # Verify final game state
        self.assertTrue(self.state._has_citadel[1])

        # Verify positions
        p1_citadel = next(a for a in self.state._deployed_assets[0] if a.definition.type == AssetType.CITADEL)
        self.assertEqual(p1_citadel.position, (0, 0))

        p1_launch = next(a for a in self.state._deployed_assets[0] if a.definition.type == AssetType.LAUNCH_SITE)
        self.assertEqual(p1_launch.position, (0, 1))

        p1_icbm = next(a for a in self.state._deployed_assets[0] if a.definition.type == AssetType.ICBM)
        self.assertEqual(p1_icbm.position, (0, 1))

        p2_citadel = next(a for a in self.state._deployed_assets[1] if a.definition.type == AssetType.CITADEL)
        self.assertEqual(p2_citadel.position, (0, 10))


if __name__ == "__main__":
    unittest.main()
