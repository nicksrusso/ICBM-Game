from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass


class MoveType(Enum):
    LAUNCH = "launch"  # Launch a mobile asset
    MOVE = "move"  # Move an asset to a new position
    SCOUT = "scout"  # Activate scouting on an asset


@dataclass
class Move:
    move_type: MoveType
    asset_id: int
    params: List[any]  # Additional parameters (e.g., target position)


def get_valid_moves(self) -> List[Move]:
    """Get list of valid moves for current player"""
    valid_moves = []

    # Check each asset owned by current player
    for asset in self.player_assets[self.current_player]:
        if asset.is_destroyed:
            continue

        # Launch moves for unlaunched mobile assets at launch sites
        if asset.definition.is_mobile and not asset.is_active and not asset.has_acted_this_turn:
            # Verify asset is at a launch site
            has_launch_site = False
            for board_asset in self.board[asset.position]:
                if board_asset.definition.type == "base" and board_asset.owner == self.current_player:
                    has_launch_site = True
                    break
            if has_launch_site:
                valid_moves.append(Move(move_type=MoveType.LAUNCH, asset_id=asset.id, params=[]))

        # Movement for active mobile assets that haven't moved
        if asset.definition.is_mobile and asset.is_active and not asset.has_moved_this_turn:
            x, y = asset.position
            # Check all positions within speed range
            for dx in range(-asset.definition.speed, asset.definition.speed + 1):
                for dy in range(-asset.definition.speed, asset.definition.speed + 1):
                    if abs(dx) + abs(dy) <= asset.definition.speed:  # Manhattan distance
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.BOARD_WIDTH and 0 <= new_y < self.BOARD_HEIGHT:
                            valid_moves.append(Move(move_type=MoveType.MOVE, asset_id=asset.id, params=[(new_x, new_y)]))

        # Scouting for assets with visibility range that haven't acted
        if asset.definition.visibility_range > 0 and not asset.has_acted_this_turn:
            valid_moves.append(Move(move_type=MoveType.SCOUT, asset_id=asset.id, params=[]))

    return valid_moves


def make_move(self, move: Move) -> bool:
    """Execute a move if valid"""
    if self.phase != 1:  # Must be in play phase
        return False

    # Find the asset
    target_asset = None
    for asset in self.player_assets[self.current_player]:
        if asset.id == move.asset_id:
            target_asset = asset
            break

    if not target_asset or target_asset.is_destroyed:
        return False

    if move.move_type == MoveType.LAUNCH:
        if not target_asset.definition.is_mobile:
            return False
        target_asset.launch()
        target_asset.has_acted_this_turn = True
        return True

    elif move.move_type == MoveType.MOVE:
        if len(move.params) != 1:
            return False
        new_pos = move.params[0]
        # Validate movement
        x, y = target_asset.position
        new_x, new_y = new_pos
        dx, dy = new_x - x, new_y - y
        if abs(dx) + abs(dy) > target_asset.definition.speed or not (
            0 <= new_x < self.BOARD_WIDTH and 0 <= new_y < self.BOARD_HEIGHT
        ):
            return False

        # Update position
        old_pos = target_asset.position
        self.board[old_pos].remove(target_asset)
        if not self.board[old_pos]:  # Clean up empty positions
            del self.board[old_pos]

        if new_pos not in self.board:
            self.board[new_pos] = []
        self.board[new_pos].append(target_asset)
        target_asset.move_to(new_pos)

        return True

    elif move.move_type == MoveType.SCOUT:
        if target_asset.definition.visibility_range <= 0:
            return False
        target_asset.has_acted_this_turn = True
        # Visibility update happens in end_turn
        return True

    return False


ICBMGame.get_valid_moves = get_valid_moves
ICBMGame.make_move = make_move
