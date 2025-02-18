from abc import ABC, abstractmethod
from typing import List, Optional
from asset import AssetType
import random


class GamePlayer(ABC):
    def __init__(self, player_id: int):
        self.player_id = player_id

    @abstractmethod
    def get_deployment_action(self, legal_actions: List[int], game_state) -> int:
        """Choose an action during deployment phase"""
        pass

    @abstractmethod
    def get_battle_actions(self, legal_actions: List[int], game_state) -> List[int]:
        """Choose actions during battle phase"""
        pass


class HumanPlayer(GamePlayer):
    def get_deployment_action(self, legal_actions: List[int], game_state):
        # Interface with UI to get human input
        pass


class RandomAIPlayer(GamePlayer):
    def get_deployment_action(self, legal_actions: List[int], game_state):
        return random.choice(legal_actions)


class LLMPlayer(GamePlayer):
    def __init__(self, player_id: int, llm_client):
        super().__init__(player_id)
        self.llm_client = llm_client
