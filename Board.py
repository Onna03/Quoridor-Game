import numpy as np
from Player import Player
from AIPlayer import AIPlayer

class Board:
    def __init__(self, size=9, vs_ai_mode=False):
        self.pawn_dim = size
        self.wall_dim = size - 1
        self.total_dim = self.pawn_dim + self.wall_dim

        self.grid = np.zeros((self.total_dim, self.total_dim), dtype=int)
        self.vs_ai = vs_ai_mode

        self.history = []
        self.redo_stack = []

        self.p1 = Player(1, self, pos=np.array([16, 8], dtype=int), objective_row=0)
        
        start_pos_p2 = np.array([0, 8], dtype=int)
        goal_p2 = self.total_dim - 1
        
        if self.vs_ai:
            self.p2 = AIPlayer(2, self, pos=start_pos_p2, objective_row=goal_p2)
        else:
            self.p2 = Player(2, self, pos=start_pos_p2, objective_row=goal_p2)

        self.active_player = self.p1

    def save_snapshot(self):
        """Saves current state to history. Does NOT clear redo stack automatically anymore."""
        snapshot = {
            "grid": self.grid.copy(),
            "p1_pos": self.p1.pos.copy(),
            "p1_walls": self.p1.walls_left,
            "p2_pos": self.p2.pos.copy(),
            "p2_walls": self.p2.walls_left,
            "active_player_id": self.active_player.id
        }
        self.history.append(snapshot)

    def clear_redo(self):
        """Explicitly clears the redo stack (call this only after a VALID move)."""
        self.redo_stack.clear()

    def undo(self):
        if not self.history: return False

        current_state = {
            "grid": self.grid.copy(),
            "p1_pos": self.p1.pos.copy(),
            "p1_walls": self.p1.walls_left,
            "p2_pos": self.p2.pos.copy(),
            "p2_walls": self.p2.walls_left,
            "active_player_id": self.active_player.id
        }
        self.redo_stack.append(current_state)

        prev = self.history.pop()
        self._apply_state(prev)
        return True

    def redo(self):
        if not self.redo_stack: return False

        current_state = {
            "grid": self.grid.copy(),
            "p1_pos": self.p1.pos.copy(),
            "p1_walls": self.p1.walls_left,
            "p2_pos": self.p2.pos.copy(),
            "p2_walls": self.p2.walls_left,
            "active_player_id": self.active_player.id
        }
        self.history.append(current_state)

        future = self.redo_stack.pop()
        self._apply_state(future)
        return True

    def _apply_state(self, state):
        self.grid = state["grid"].copy()
        self.p1.pos = state["p1_pos"].copy()
        self.p1.walls_left = state["p1_walls"]
        self.p2.pos = state["p2_pos"].copy()
        self.p2.walls_left = state["p2_walls"]
        
        if state["active_player_id"] == 1:
            self.active_player = self.p1
        else:
            self.active_player = self.p2

    def get_snapshot(self):
        return [
            [self.p1.pos.copy(), self.p1.walls_left],
            [self.p2.pos.copy(), self.p2.walls_left],
            self.grid.copy()
        ]