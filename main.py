import pygame
import sys
import threading
import math
import os
from Board import Board
from Config import THEME, HORIZONTAL, VERTICAL

# Center the window
os.environ['SDL_VIDEO_CENTERED'] = '1'

class GameGUI:
    def __init__(self, vs_ai=True):
        pygame.init()
        self.screen_w, self.screen_h = 800, 600
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("QUORIDOR")
        
        self.board_logic = Board(vs_ai_mode=vs_ai)
        self.clock = pygame.time.Clock()
        
        self.font_ui = pygame.font.SysFont("consolas", 18)
        self.font_title = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_win = pygame.font.SysFont("consolas", 50, bold=True)

        self.margin = 15
        self.game_size = min(self.screen_h, self.screen_w) * 0.70 
        
        self.start_x = (self.screen_w - self.game_size) // 2
        self.start_y = (self.screen_h - self.game_size) // 2 + 20
        
        self.cell_size = int((self.game_size - (10 * self.margin)) / 9)
        
        self.hover_node = None
        self.wall_anchor = None
        
        self.running = True
        self.ai_thinking = False
        self.winner = None
        self.err_msg = ""
        self.err_time = 0
        self.blur_bg = None 

        btn_w, btn_h = 200, 60
        self.exit_btn_rect = pygame.Rect(
            (self.screen_w - btn_w) // 2,
            (self.screen_h // 2) + 50,
            btn_w, btn_h
        )

    def to_screen_coords(self, grid_x, grid_y):
        pixel_x = self.start_x + self.margin
        for i in range(grid_x):
            pixel_x += self.cell_size if i % 2 == 0 else self.margin
            
        pixel_y = self.start_y + self.margin
        for i in range(grid_y):
            pixel_y += self.cell_size if i % 2 == 0 else self.margin
            
        w = self.cell_size if grid_x % 2 == 0 else self.margin
        h = self.cell_size if grid_y % 2 == 0 else self.margin
        return pixel_x, pixel_y, w, h

    def get_grid_from_mouse(self, mx, my):
        total_dim = self.board_logic.total_dim
        for r in range(total_dim):
            for c in range(total_dim):
                px, py, w, h = self.to_screen_coords(c, r)
                rect = pygame.Rect(px, py, w, h)
                if rect.collidepoint(mx, my):
                    return c, r
        return None

    def draw_glow_circle(self, surf, color, center, radius):
        for i in range(3):
            c = pygame.Color(color)
            pygame.draw.circle(surf, (c.r, c.g, c.b, 50), center, radius + 4 - i)
        pygame.draw.circle(surf, pygame.Color(color), center, radius)
        pygame.draw.circle(surf, (255, 255, 255), center, radius - 4)

    def draw(self):
        if self.winner:
            self.draw_game_over()
            pygame.display.flip()
            return

        self.screen.fill(pygame.Color(THEME["background"]))
        
        bg_rect = pygame.Rect(self.start_x, self.start_y, self.game_size, self.game_size)
        pygame.draw.rect(self.screen, pygame.Color(THEME["board_bg"]), bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, pygame.Color(THEME["grid_lines"]), bg_rect, 2, border_radius=10)

        total_dim = self.board_logic.total_dim
        for r in range(total_dim):
            for c in range(total_dim):
                px, py, w, h = self.to_screen_coords(c, r)
                val = self.board_logic.grid[r, c]
                is_cell = (r % 2 == 0 and c % 2 == 0)
                is_wall_slot = not is_cell
                
                if is_cell:
                    pygame.draw.rect(self.screen, (30, 30, 30), (px, py, w, h), border_radius=4)
                    if self.hover_node == (c, r) and self.board_logic.active_player.id == 1 and not self.ai_thinking:
                        pygame.draw.rect(self.screen, (50, 50, 50), (px, py, w, h), border_radius=4)
                    if val == 1:
                        self.draw_glow_circle(self.screen, THEME["p1_color"], (px+w//2, py+h//2), w//3)
                    elif val == 2:
                        self.draw_glow_circle(self.screen, THEME["p2_color"], (px+w//2, py+h//2), w//3)
                elif is_wall_slot and val != 0:
                    pygame.draw.rect(self.screen, pygame.Color(THEME["wall_color"]), (px, py, w, h))

        if self.wall_anchor:
            ax, ay = self.wall_anchor
            if self.hover_node:
                hx, hy = self.hover_node
                if abs(ax - hx) == 2 or abs(ay - hy) == 2:
                    px1, py1, w1, h1 = self.to_screen_coords(ax, ay)
                    px2, py2, w2, h2 = self.to_screen_coords(hx, hy)
                    cx, cy = (ax+hx)//2, (ay+hy)//2
                    pc, pyc, wc, hc = self.to_screen_coords(cx, cy)
                    s = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
                    c_rgba = (57, 255, 20, 100)
                    pygame.draw.rect(s, c_rgba, (px1, py1, w1, h1))
                    pygame.draw.rect(s, c_rgba, (px2, py2, w2, h2))
                    pygame.draw.rect(s, c_rgba, (pc, pyc, wc, hc))
                    self.screen.blit(s, (0,0))

        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        p1 = self.board_logic.p1
        p2 = self.board_logic.p2
        
        # Stats in top corners
        lbl_p1 = self.font_ui.render(f"P1 WALLS: {p1.walls_left}", True, pygame.Color(THEME["p1_color"]))
        self.screen.blit(lbl_p1, (self.start_x, 20))
        
        lbl_p2 = self.font_ui.render(f"P2 WALLS: {p2.walls_left}", True, pygame.Color(THEME["p2_color"]))
        self.screen.blit(lbl_p2, (self.screen_w - self.start_x - lbl_p2.get_width(), 20))

        if self.ai_thinking:
            msg, col = ">> AI THINKING...", "#FFFFFF"
        else:
            turn = "P1" if self.board_logic.active_player.id == 1 else "P2"
            msg, col = f">> TURN: {turn}", THEME["p1_color"] if turn == "P1" else THEME["p2_color"]
            
        status = self.font_title.render(msg, True, pygame.Color(col))
        
        # VISUAL FIX: Moved 'TURN' text down to Y=60 so it doesn't overlap walls
        self.screen.blit(status, (self.screen_w//2 - status.get_width()//2, 60))
        
        hint = self.font_ui.render("[Ctrl+Z] Undo  [Ctrl+Y] Redo", True, (100, 100, 100))
        self.screen.blit(hint, (self.screen_w//2 - hint.get_width()//2, self.screen_h - 40))

        if pygame.time.get_ticks() < self.err_time:
            err = self.font_ui.render(f"[!] {self.err_msg}", True, (255, 50, 50))
            self.screen.blit(err, (self.screen_w//2 - err.get_width()//2, self.screen_h - 80))

    def draw_game_over(self):
        if self.blur_bg is None:
            snapshot = self.screen.copy()
            small_w, small_h = self.screen_w // 10, self.screen_h // 10
            small_snap = pygame.transform.smoothscale(snapshot, (small_w, small_h))
            self.blur_bg = pygame.transform.smoothscale(small_snap, (self.screen_w, self.screen_h))
            
            darken = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            darken.fill((0, 0, 0, 150))
            self.blur_bg.blit(darken, (0, 0))

        self.screen.blit(self.blur_bg, (0, 0))

        win_color = THEME["p1_color"] if "PLAYER 1" in self.winner else THEME["p2_color"]
        txt = self.font_win.render(f"{self.winner} WINS!", True, pygame.Color(win_color))
        self.screen.blit(txt, (self.screen_w//2 - txt.get_width()//2, self.screen_h//2 - 50))

        mx, my = pygame.mouse.get_pos()
        hover = self.exit_btn_rect.collidepoint(mx, my)
        btn_color = (200, 50, 50) if hover else (150, 30, 30)
        
        pygame.draw.rect(self.screen, btn_color, self.exit_btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.exit_btn_rect, 2, border_radius=10)
        
        btn_txt = self.font_title.render("EXIT GAME", True, (255, 255, 255))
        self.screen.blit(btn_txt, (
            self.exit_btn_rect.centerx - btn_txt.get_width()//2, 
            self.exit_btn_rect.centery - btn_txt.get_height()//2
        ))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.winner and event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_btn_rect.collidepoint(event.pos):
                    self.running = False 
            
            if not self.winner:
                if event.type == pygame.KEYDOWN:
                    if event.mod & pygame.KMOD_CTRL:
                        if event.key == pygame.K_z and not self.ai_thinking:
                            if self.board_logic.undo():
                                self.wall_anchor = None
                                if self.board_logic.vs_ai: self.board_logic.undo()
                        if event.key == pygame.K_y and not self.ai_thinking:
                            if self.board_logic.redo():
                                if self.board_logic.vs_ai: self.board_logic.redo()

                if event.type == pygame.KEYDOWN and not self.ai_thinking:
                    if self.board_logic.vs_ai and self.board_logic.active_player.id == 2: continue
                    
                    keys = {
                        pygame.K_UP: "top", pygame.K_DOWN: "down",
                        pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
                        pygame.K_q: "topLeft", pygame.K_e: "topRight",
                        pygame.K_z: "bottomLeft", pygame.K_c: "bottomRight"
                    }
                    
                    if event.key in keys:
                        self.board_logic.save_snapshot() # Save state
                        moved = self.board_logic.active_player.handle_move_request(keys[event.key])
                        if moved:
                            self.board_logic.clear_redo()
                            self.end_turn()
                        else:
                            self.board_logic.history.pop() # Invalid move, revert history

                if event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    mx, my = pygame.mouse.get_pos()
                    grid_pos = self.get_grid_from_mouse(mx, my)
                    
                    if grid_pos:
                        cx, cy = grid_pos
                        is_wall_slot = (cx % 2 != 0 or cy % 2 != 0)
                        
                        if is_wall_slot and self.board_logic.active_player.walls_left > 0:
                            if not self.wall_anchor:
                                self.wall_anchor = (cx, cy)
                            else:
                                ax, ay = self.wall_anchor
                                if (abs(ax - cx) == 2 and ay == cy) or (abs(ay - cy) == 2 and ax == cx):
                                    mid_x, mid_y = (ax+cx)//2, (ay+cy)//2
                                    coords = [(ay, ax), (mid_y, mid_x), (cy, cx)]
                                    
                                    self.board_logic.save_snapshot() # Save state
                                    p = self.board_logic.active_player
                                    if all(self.board_logic.grid[r, c] == 0 for r, c in coords):
                                        for r, c in coords: self.board_logic.grid[r, c] = 1
                                        
                                        if p.has_path_to_goal(self.board_logic.grid) and \
                                           self.board_logic.p2.has_path_to_goal(self.board_logic.grid) and \
                                           self.board_logic.p1.has_path_to_goal(self.board_logic.grid):
                                            
                                            self.board_logic.grid[mid_y, mid_x] = HORIZONTAL if ay == cy else VERTICAL
                                            p.walls_left -= 1
                                            self.board_logic.clear_redo()
                                            self.end_turn()
                                        else:
                                            for r, c in coords: self.board_logic.grid[r, c] = 0
                                            self.board_logic.history.pop()
                                            self.show_err("Blocks Path!")
                                    else:
                                        self.board_logic.history.pop()
                                        self.show_err("Occupied!")
                                else:
                                    self.show_err("Invalid Shape")
                                self.wall_anchor = None
                        elif not is_wall_slot:
                            self.wall_anchor = None

    def end_turn(self):
        p1_win = (self.board_logic.p1.pos[0] == 0)
        p2_win = (self.board_logic.p2.pos[0] == 16)
        
        if p1_win: self.winner = "PLAYER 1"
        elif p2_win: self.winner = "PLAYER 2"
        
        if self.board_logic.active_player == self.board_logic.p1 and not self.winner:
            self.board_logic.active_player = self.board_logic.p2
            if self.board_logic.vs_ai:
                self.ai_thinking = True
                threading.Thread(target=self.run_ai).start()
        elif not self.winner:
            self.board_logic.active_player = self.board_logic.p1

    def run_ai(self):
        self.board_logic.save_snapshot()
        self.board_logic.p2.ai_move()
        self.board_logic.clear_redo()
        self.ai_thinking = False
        self.end_turn()

    def show_err(self, msg):
        self.err_msg = msg
        self.err_time = pygame.time.get_ticks() + 2000

    def main_loop(self):
        while self.running:
            mx, my = pygame.mouse.get_pos()
            self.hover_node = self.get_grid_from_mouse(mx, my)
            self.handle_input()
            self.draw()
            self.clock.tick(60)

class Menu:
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((500, 400))
        pygame.display.set_caption("QUORIDOR // LAUNCH")
        font = pygame.font.SysFont("consolas", 30)
        
        btn_ai = pygame.Rect(100, 100, 300, 60)
        btn_pvp = pygame.Rect(100, 200, 300, 60)
        
        while True:
            screen.fill((10, 10, 10))
            mx, my = pygame.mouse.get_pos()
            c_ai = (50, 50, 50) if not btn_ai.collidepoint(mx, my) else (80, 80, 80)
            c_pvp = (50, 50, 50) if not btn_pvp.collidepoint(mx, my) else (80, 80, 80)
            
            pygame.draw.rect(screen, c_ai, btn_ai, border_radius=5)
            pygame.draw.rect(screen, c_pvp, btn_pvp, border_radius=5)
            pygame.draw.rect(screen, pygame.Color(THEME["p2_color"]), btn_ai, 2, border_radius=5)
            pygame.draw.rect(screen, pygame.Color(THEME["p1_color"]), btn_pvp, 2, border_radius=5)
            
            t1 = font.render("VS COMPUTER", True, (255, 255, 255))
            t2 = font.render("VS HUMAN", True, (255, 255, 255))
            screen.blit(t1, (btn_ai.centerx - t1.get_width()//2, btn_ai.centery - t1.get_height()//2))
            screen.blit(t2, (btn_pvp.centerx - t2.get_width()//2, btn_pvp.centery - t2.get_height()//2))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_ai.collidepoint(event.pos): return True
                    if btn_pvp.collidepoint(event.pos): return False
            pygame.display.flip()

if __name__ == "__main__":
    mode = Menu().run()
    game = GameGUI(vs_ai=mode)
    game.main_loop()