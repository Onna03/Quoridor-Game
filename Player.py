from collections import deque
from Config import THEME

class Player:
    def __init__(self, pid, board_ref, pos, objective_row, walls=10):
        self.id = pid
        self.objective_row = objective_row
        self.pos = pos
        self.walls_left = walls
        self.board = board_ref
        
        self.board.grid[self.pos[0], self.pos[1]] = self.id
        self.color = THEME["p1_color"] if self.id == 1 else THEME["p2_color"]

    def handle_move_request(self, direction_key):
        """Maps string inputs to logic checks."""
        move_map = {
            "top":    lambda: self._check_orthogonal(0, -1),
            "down":   lambda: self._check_orthogonal(0, 1),
            "left":   lambda: self._check_orthogonal(1, -1),
            "right":  lambda: self._check_orthogonal(1, 1),
            "topLeft":     lambda: self._check_diagonal(-1, -1),
            "topRight":    lambda: self._check_diagonal(1, -1),
            "bottomLeft":  lambda: self._check_diagonal(-1, 1),
            "bottomRight": lambda: self._check_diagonal(1, 1),
        }

        if direction_key in move_map and move_map[direction_key]():
            return True
        print(f"Move '{direction_key}' blocked or invalid.")
        return False

    def _check_orthogonal(self, axis, step):
        r, c = self.pos
        if axis == 0:
            wall_r, wall_c = r + step, c
            dest_r, dest_c = r + 2 * step, c
        else: 
            wall_r, wall_c = r, c + step
            dest_r, dest_c = r, c + 2 * step

        if not (0 <= dest_r < self.board.total_dim and 0 <= dest_c < self.board.total_dim):
            return False

        if self.board.grid[wall_r, wall_c] != 0:
            return False

        if self.board.grid[dest_r, dest_c] != 0:
            return self._try_jump(axis, step)

        self._update_pos(dest_r, dest_c)
        return True

    def _try_jump(self, axis, step):
        r, c = self.pos
        if axis == 0:
            jump_r = r + 4 * step
            if 0 <= jump_r < self.board.total_dim and self.board.grid[r + 3 * step, c] == 0:
                self._update_pos(jump_r, c)
                return True
        else: 
            jump_c = c + 4 * step
            if 0 <= jump_c < self.board.total_dim and self.board.grid[r, c + 3 * step] == 0:
                self._update_pos(r, jump_c)
                return True
        return False

    def _check_diagonal(self, x_dir, y_dir):
        """Diagonal moves are only valid if a straight jump is blocked by a wall or board edge."""
        r, c = self.pos
        dest_r, dest_c = r + 2 * y_dir, c + 2 * x_dir

        if not (0 <= dest_r < self.board.total_dim and 0 <= dest_c < self.board.total_dim):
            return False

        neighbor_y = self.board.grid[r + 2 * y_dir, c] != 0 if 0 <= r + 2 * y_dir < self.board.total_dim else False
        neighbor_x = self.board.grid[r, c + 2 * x_dir] != 0 if 0 <= c + 2 * x_dir < self.board.total_dim else False

        can_move = False

        if neighbor_x:
            jump_dest_x = c + 4 * x_dir
            wall_behind_opponent = self.board.grid[r, c + 3 * x_dir] if 0 <= c + 3 * x_dir < self.board.total_dim else 0
            
            is_jump_blocked = (jump_dest_x < 0 or jump_dest_x >= self.board.total_dim or wall_behind_opponent != 0)
            
            wall_to_diag = self.board.grid[r + y_dir, c + 2 * x_dir] == 0
            
            if is_jump_blocked and wall_to_diag:
                can_move = True

        if neighbor_y and not can_move:
            jump_dest_y = r + 4 * y_dir
            wall_behind_opponent = self.board.grid[r + 3 * y_dir, c] if 0 <= r + 3 * y_dir < self.board.total_dim else 0
            
            is_jump_blocked = (jump_dest_y < 0 or jump_dest_y >= self.board.total_dim or wall_behind_opponent != 0)
            wall_to_diag = self.board.grid[r + 2 * y_dir, c + x_dir] == 0
            
            if is_jump_blocked and wall_to_diag:
                can_move = True

        if can_move:
            self._update_pos(dest_r, dest_c)
            return True
        return False

    def _update_pos(self, r, c):
        self.board.grid[self.pos[0], self.pos[1]] = 0
        self.pos = [r, c]
        self.board.grid[r, c] = self.id

    def has_path_to_goal(self, test_grid):
        """BFS to verify if a path exists to the objective row."""
        start_node = tuple(self.pos)
        queue = deque([start_node])
        seen = {start_node}
        
        steps = [
            ((-2, 0), (-1, 0)), ((2, 0), (1, 0)), 
            ((0, -2), (0, -1)), ((0, 2), (0, 1))
        ]

        while queue:
            cy, cx = queue.popleft()
            if cy == self.objective_row:
                return True

            for (dy, dx), (wy, wx) in steps:
                ny, nx = cy + dy, cx + dx
                wall_y, wall_x = cy + wy, cx + wx

                if 0 <= ny < self.board.total_dim and 0 <= nx < self.board.total_dim:
                    if test_grid[wall_y, wall_x] == 0 and test_grid[ny, nx] == 0:
                        if (ny, nx) not in seen:
                            seen.add((ny, nx))
                            queue.append((ny, nx))
        return False