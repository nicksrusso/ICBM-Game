import os
import pathlib
from icbm_game import ICBMGame


def get_asset_definition_path() -> str:
    """Get the path to asset definitions file"""
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


def get_game_config_path() -> str:
    env_path = os.environ.get("GAME_CONF")
    if env_path:
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"Game config file specified in GAME_CONF not found: {env_path}")
        return env_path

    # If no environment variable, construct default path
    current_file = pathlib.Path(__file__)
    default_path = current_file.parent.parent / "game_rules" / "game_config.json"

    if not default_path.exists():
        raise FileNotFoundError(f"Default game config file not found at: {default_path}")

    return str(default_path)


def test_deployment():
    game = ICBMGame(asset_config_path=get_asset_definition_path(), game_config_path=get_game_config_path())

    print("Initial affordable assets:")
    for name, count in game.get_deployable_assets().items():
        print(f"  {name}: can afford {count}")

    print("\nTesting deployment:")

    # Deploy launch site
    result = game.deploy_asset("LAUNCH_SITE", 5, 5)
    print(f"Deploy LAUNCH_SITE at (5,5): {'Success' if result else 'Failed'}")

    # Now try ICBM again
    result = game.deploy_asset("ICBM", 5, 5)
    print(f"Deploy ICBM at launch site: {'Success' if result else 'Failed'}")

    result = game.deploy_asset("CITADEL", 0, 0)

    print(f"\nCurrent points: {game.points[game.current_player]}")
    print(f"Valid deployment: {game.is_valid_deployment()}")


if __name__ == "__main__":
    test_deployment()
