from Player import Player
from Config import TYPE_PAWN, TYPE_WALL, HORIZONTAL, VERTICAL
import math
from collections import deque
import heapq

class AIPlayer(Player):
    def __init__(self, *args, search_depth=1, wall_bonus_weight=1.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = search_depth
        self.wall_weight = wall_bonus_weight

    def ai_move(self):
        """Main entry point for AI decision making."""
        state = self.board.get_snapshot()
        
        valid_moves = self._get_moves(state, is_max=True)
        
        for m in valid_moves:
            if m[0] == TYPE_PAWN and m[1][0] == self.objective_row:
                self._apply_move_real(m)
                return

        best_val = -math.inf
        best_move = None

        for move in valid_moves:
            next_state = self._simulate_move(state, move, is_max=True)
            val = self._minimax(next_state, self.depth, -math.inf, math.inf, False)
            if val > best_val:
                best_val = val
                best_move = move

        if best_move:
            self._apply_move_real(best_move)

    def _minimax(self, state, depth, alpha, beta, is_max):
        p1_pos, p2_pos = state[0][0], state[1][0]
        
        if p1_pos[0] == self.board.p1.objective_row: return -math.inf
        if p2_pos[0] == self.objective_row: return math.inf
        
        if depth == 0:
            return self._heuristic(state)

        moves = self._get_moves(state, is_max)
        
        moves.sort(key=lambda m: 0 if m[0] == TYPE_PAWN else 1)

        if is_max:
            max_eval = -math.inf
            for move in moves:
                sim_state = self._simulate_move(state, move, True)
                eval = self._minimax(sim_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                sim_state = self._simulate_move(state, move, False)
                eval = self._minimax(sim_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

    def _apply_move_real(self, move):
        """Executes the chosen move on the actual game board."""
        if move[0] == TYPE_PAWN:
            self.board.grid[self.pos[0], self.pos[1]] = 0
            self.pos = move[1]
            self.board.grid[self.pos[0], self.pos[1]] = self.id
        else:
            c1, c2, c3 = move[1]
            self.board.grid[c1[0], c1[1]] = 1
            self.board.grid[c2[0], c2[1]] = HORIZONTAL if c1[0] == c2[0] else VERTICAL
            self.board.grid[c3[0], c3[1]] = 1
            self.walls_left -= 1

    def _simulate_move(self, state, move, is_max):
        """Returns a new state list with the move applied (Virtual)."""
        new_state = [
            [state[0][0].copy(), state[0][1]],
            [state[1][0].copy(), state[1][1]],
            state[2].copy()
        ]
        
        idx = 1 if is_max else 0
        
        if move[0] == TYPE_PAWN:
            old_r, old_c = new_state[idx][0]
            new_state[2][old_r, old_c] = 0
            new_state[idx][0] = move[1]
            new_r, new_c = move[1]
            pid = 2 if is_max else 1
            new_state[2][new_r, new_c] = pid
        else:
            c1, c2, c3 = move[1]
            new_state[2][c1[0], c1[1]] = 1
            connector = HORIZONTAL if c1[0] == c2[0] else VERTICAL
            new_state[2][c2[0], c2[1]] = connector
            new_state[2][c3[0], c3[1]] = 1
            new_state[idx][1] -= 1 
            
        return new_state

    def _get_moves(self, state, is_max):
        """Generates all legal moves for the virtual state."""
        moves = []
        grid = state[2]
        my_idx = 1 if is_max else 0
        opp_idx = 0 if is_max else 1
        
        pos = state[my_idx][0]
        opp_pos = state[opp_idx][0]
        walls = state[my_idx][1]
        
        r, c = pos
        dim = self.board.total_dim
        
        steps = [(-2,0,-1,0), (2,0,1,0), (0,-2,0,-1), (0,2,0,1)]
        
        for dr, dc, wr, wc in steps:
            nr, nc = r+dr, c+dc
            wall_r, wall_c = r+wr, c+wc
            
            if 0 <= nr < dim and 0 <= nc < dim:
                if 0 <= wall_r < dim and 0 <= wall_c < dim and grid[wall_r, wall_c] == 0:
                    if (nr, nc) == (tuple(opp_pos)):
                        jr, jc = nr+dr, nc+dc
                        jw_r, jw_c = nr+wr, nc+wc
                        if 0 <= jr < dim and 0 <= jc < dim and grid[jw_r, jw_c] == 0:
                            moves.append((TYPE_PAWN, [jr, jc]))
                        else:
                            pass 
                    else:
                        moves.append((TYPE_PAWN, [nr, nc]))

        if walls > 0:
            for y in range(1, dim-1, 2):
                for x in range(1, dim-1, 2):
                    orientations = [
                        [(y, x-1), (y, x), (y, x+1)], 
                        [(y-1, x), (y, x), (y+1, x)]  
                    ]
                    for coords in orientations:
                        if all(grid[wy, wx] == 0 for wy, wx in coords):
                            test_grid = grid.copy()
                            for wy, wx in coords: test_grid[wy, wx] = 1
                            
                            if self._has_path(test_grid, state[0][0], self.board.p1.objective_row) and \
                               self._has_path(test_grid, state[1][0], self.objective_row):
                                moves.append((TYPE_WALL, coords))
                                
        return moves

    def _has_path(self, grid, start, goal_row):
        q = deque([tuple(start)])
        seen = {tuple(start)}
        dim = self.board.total_dim
        while q:
            r, c = q.popleft()
            if r == goal_row: return True
            for dr, dc, wr, wc in [(-2,0,-1,0), (2,0,1,0), (0,-2,0,-1), (0,2,0,1)]:
                nr, nc = r+dr, c+dc
                w_r, w_c = r+wr, c+wc
                if 0 <= nr < dim and 0 <= nc < dim:
                    if grid[w_r, w_c] == 0 and grid[nr, nc] == 0:
                        if (nr, nc) not in seen:
                            seen.add((nr, nc))
                            q.append((nr, nc))
        return False

    def _heuristic(self, state):
        p1_r, p1_c = state[0][0]
        p2_r, p2_c = state[1][0]
        
        dist_p1 = abs(p1_r - self.board.p1.objective_row)
        dist_p2 = abs(p2_r - self.objective_row)
        
        score = dist_p1 - dist_p2
        
        score += state[1][1] * self.wall_weight
        return score