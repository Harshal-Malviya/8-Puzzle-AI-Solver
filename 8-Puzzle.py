import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import heapq
import copy
from collections import deque
import json
import time
import threading
import os 

# this project uses the 'playsound' library for sound effects.
# to install it, run this command in your terminal:
# pip install playsound==1.2.2
try:
    from playsound import playsound
except ImportError:
    print("playsound library not found, so sound effects will be disabled.")
    print("to enable sound, run: pip install playsound==1.2.2")
    playsound = None

# game constants
GOAL_STATE = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
BOARD_SIZE = 3
EMPTY_TILE = 0

# ui layout constants
TILE_SIZE = 120
TILE_PADDING = 10
CORNER_RADIUS = 24
ELEVATION_OFFSET = 4

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle AI Pro")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.is_animating = False
        self.sound_enabled = playsound is not None

        self._initialize_colors_and_styles()
        self.board = copy.deepcopy(GOAL_STATE)
        
        main_frame = ttk.Frame(root, padding="15", style="App.TFrame")
        main_frame.pack(expand=True, fill=tk.BOTH)

        self._create_info_panel(main_frame)
        self._create_game_board(main_frame)
        self._create_control_panel(main_frame)
        
        self.new_game()

    def _initialize_colors_and_styles(self):
        # sets up the material 3 inspired color palette and widget styles
        self.colors = {
            "background": "#f3f0f7", "surface": "#e7e0ec", "primary": "#6750a4",
            "on_primary": "#ffffff", "tile_text": "#1d1b20", "shadow": "#d8d3df",
            "hint": "#b5ff91" # bright green for the hint highlight
        }
        self.tile_colors = {
            1: "#e9dff7", 2: "#ead8f7", 3: "#ebd6f8", 4: "#eed1f9",
            5: "#f1ccfa", 6: "#f4c7fb", 7: "#f7c2fc", 8: "#facdfd"
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("App.TFrame", background=self.colors["background"])
        style.configure("TLabel", background=self.colors["background"], foreground=self.colors["tile_text"], font=("Roboto Medium", 16))
        style.configure("TLabelframe", background=self.colors["background"])
        style.configure("TLabelframe.Label", background=self.colors["background"], foreground=self.colors["primary"], font=("Roboto Medium", 14, "bold"))
        
        style.configure("M3.TButton", font=("Roboto Medium", 13, "bold"), padding=14, borderwidth=0, relief="flat", background=self.colors["primary"], foreground=self.colors["on_primary"])
        style.map("M3.TButton", background=[('active', '#5A4491'), ('pressed', '#4F3781')])

    def _create_info_panel(self, parent):
        # creates the top panel for showing moves and time
        info_frame = ttk.Frame(parent, style="App.TFrame")
        info_frame.pack(pady=10, fill=tk.X)
        self.moves_label = ttk.Label(info_frame, text="Moves: 0")
        self.moves_label.pack(side=tk.LEFT, expand=True)
        self.time_label = ttk.Label(info_frame, text="Time: 0s")
        self.time_label.pack(side=tk.RIGHT, expand=True)

    def _create_game_board(self, parent):
        # creates the main canvas where the puzzle is drawn
        canvas_size = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE + 1) * TILE_PADDING
        self.canvas = tk.Canvas(parent, width=canvas_size, height=canvas_size, bg=self.colors["surface"], highlightthickness=0)
        self.canvas.pack(pady=15)
        self.canvas.bind("<Button-1>", self._canvas_click_handler)
        self.tile_items = {} # stores canvas item ids for each tile's parts

    def _create_control_panel(self, parent):
        # creates the bottom panel with all the user controls
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="15")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # row 0: algorithm selection
        ttk.Label(control_frame, text="Algorithm:", font=("Roboto", 13)).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.algo_var = tk.StringVar(value="A* (Manhattan)")
        algo_menu = ttk.OptionMenu(control_frame, self.algo_var, "A* (Manhattan)", "A* (Manhattan)", "A* (Misplaced)", "BFS")
        algo_menu.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # row 1: main action buttons
        self.solve_button = ttk.Button(control_frame, text="Solve", command=self.auto_solve, style="M3.TButton")
        self.solve_button.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.new_game_button = ttk.Button(control_frame, text="New Puzzle", command=self.new_game, style="M3.TButton")
        self.new_game_button.grid(row=1, column=2, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # row 2: hint and save/load
        self.hint_button = ttk.Button(control_frame, text="Hint", command=self.get_hint, style="M3.TButton")
        self.hint_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.save_button = ttk.Button(control_frame, text="Save", command=self.save_game, style="M3.TButton")
        self.save_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.load_button = ttk.Button(control_frame, text="Load", command=self.load_game, style="M3.TButton")
        self.load_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        for i in range(4): control_frame.columnconfigure(i, weight=1)

    def redraw_board(self, hint_tile_val=None):
        # redraws the entire board, optionally highlighting a tile for the hint
        self.canvas.delete("all")
        self.tile_items.clear()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                val = self.board[i][j]
                if val != EMPTY_TILE:
                    x1, y1, x2, y2 = self._get_coords(i, j)
                    
                    shadow_color = self.colors["hint"] if val == hint_tile_val else self.colors["shadow"]
                    shadow = self._create_rounded_rectangle(x1, y1 + ELEVATION_OFFSET, x2, y2 + ELEVATION_OFFSET, CORNER_RADIUS, fill=shadow_color, width=0)
                    rect = self._create_rounded_rectangle(x1, y1, x2, y2, CORNER_RADIUS, fill=self.tile_colors[val], width=0)
                    text = self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=str(val), font=("Roboto Medium", 48, "bold"), fill=self.colors["tile_text"])
                    
                    self.tile_items[val] = (rect, shadow, text)

    def _play_sound(self, sound_file):
        # plays a sound in a separate thread to avoid freezing the ui
        # checks if the file exists first to prevent crashing
        if self.sound_enabled and os.path.exists(sound_file):
            threading.Thread(target=lambda: playsound(sound_file), daemon=True).start()

    def move_tile(self, r, c, is_auto_move=False):
        # handles the logic for moving a tile when clicked
        if not self.timer_running and not is_auto_move: self.start_timer()
        
        blank_r, blank_c = self.find_blank(self.board)
        is_valid_move = (abs(blank_r - r) == 1 and blank_c == c) or \
                        (abs(blank_c - c) == 1 and blank_r == r)

        if is_valid_move:
            self._play_sound("slide.wav")
            self.is_animating = True
            tile_val = self.board[r][c]
            
            item_ids = self.tile_items[tile_val]

            def on_animation_finish():
                # this function is called after the tile sliding animation completes
                self.board[blank_r][blank_c], self.board[r][c] = self.board[r][c], self.board[blank_r][blank_c]
                self.is_animating = False
                
                if not is_auto_move:
                    self.moves += 1
                    self.moves_label.config(text=f"Moves: {self.moves}")
                    self.redraw_board() # redraw to fix layering issues after move
                    if self.check_win():
                        self.stop_timer()
                        self._play_sound("solve.wav")
                        messagebox.showinfo("Congratulations!", f"You solved it in {self.moves} moves and {self.time_elapsed}s!")
                else: # this was an ai move
                    if hasattr(self, '_animation_callback'):
                        self._animation_callback()
            
            self._animate_tile_slide(item_ids, (r,c), (blank_r, blank_c), on_animation_finish)

    def update_timer(self):
        # updates the timer label every second
        if self.timer_running:
            self.time_elapsed += 1
            self.time_label.config(text=f"Time: {self.time_elapsed}s")
            self._play_sound("tick.wav")
            self.root.after(1000, self.update_timer)

    def auto_solve(self):
        # starts the automatic solving process
        self.solve_button['state'] = tk.DISABLED
        self.new_game_button['state'] = tk.DISABLED
        self.reset_stats()
        self.start_timer()

        choice = self.algo_var.get()
        start_time = time.time()
        
        if "Manhattan" in choice:
            path, stats = self._solve_astar(self.manhattan_distance)
        elif "Misplaced" in choice:
            path, stats = self._solve_astar(self.misplaced_tiles)
        else:
            path, stats = self._solve_bfs()

        search_time = time.time() - start_time
        
        if path:
            self.solution_path = path
            self.solution_stats = stats
            self.solution_stats["search_time"] = search_time
            self.animate_solution_step(0)
        else:
            self.stop_timer()
            messagebox.showerror("Error", "Could not find a solution!")
            self.solve_button['state'] = tk.NORMAL
            self.new_game_button['state'] = tk.NORMAL
    
    def animate_solution_step(self, index):
        # animates one step of the ai's solution path
        self.moves_label.config(text=f"Moves: {index}")
        if index >= len(self.solution_path):
            self.stop_timer()
            self._play_sound("solve.wav")
            stats = self.solution_stats
            message = (f"AI solved the puzzle!\n\n"
                       f"Path Length: {len(self.solution_path)} moves\n"
                       f"States Explored: {stats['nodes_expanded']}\n"
                       f"Search Time: {stats['search_time']:.4f} seconds")
            messagebox.showinfo("Solved!", message)
            self.solve_button['state'] = tk.NORMAL
            self.new_game_button['state'] = tk.NORMAL
            self.is_animating = False
            return
        
        next_board_state = self.solution_path[index]
        current_blank_r, current_blank_c = self.find_blank(self.board)
        next_blank_r, next_blank_c = self.find_blank(next_board_state)
        tile_to_move_r, tile_to_move_c = next_blank_r, next_blank_c

        self._animation_callback = lambda: self.animate_solution_step(index + 1)
        self.move_tile(tile_to_move_r, tile_to_move_c, is_auto_move=True)
    
    def _solve_astar(self, heuristic):
        # a* search algorithm, now returns path and performance stats
        nodes_expanded = 0
        start_node = self.board
        open_set = []
        heapq.heappush(open_set, (heuristic(start_node), 0, start_node, []))
        visited = set()

        while open_set:
            _, cost_so_far, current_board, path = heapq.heappop(open_set)
            nodes_expanded += 1
            
            if self.board_to_tuple(current_board) in visited: continue
            visited.add(self.board_to_tuple(current_board))

            if current_board == GOAL_STATE:
                return path, {"nodes_expanded": nodes_expanded}
            
            for neighbor in self._get_neighbors(current_board):
                 if self.board_to_tuple(neighbor) not in visited:
                    new_cost = cost_so_far + 1
                    f_score = new_cost + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score, new_cost, neighbor, path + [neighbor]))
        return None, {"nodes_expanded": nodes_expanded}

    def get_hint(self):
        # shows the user the next best move
        if self.is_animating: return
        self.is_animating = True
        
        path, _ = self._solve_astar(self.manhattan_distance)
        
        if not path:
            messagebox.showinfo("Hint", "The puzzle is already solved or unsolvable.")
            self.is_animating = False
            return
            
        next_move_board = path[0]
        
        blank_r, blank_c = self.find_blank(self.board)
        hint_tile_val = next_move_board[blank_r][blank_c]
        
        self.redraw_board(hint_tile_val=hint_tile_val)
        self.root.after(1000, lambda: (self.redraw_board(), setattr(self, 'is_animating', False)))

    def save_game(self):
        # saves the current game state to a json file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path: return
        
        game_state = {
            "board": self.board,
            "moves": self.moves,
            "time_elapsed": self.time_elapsed
        }
        with open(file_path, 'w') as f:
            json.dump(game_state, f)
        messagebox.showinfo("Save Game", "Game state saved successfully!")

    def load_game(self):
        # loads a game state from a json file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path: return
        
        try:
            with open(file_path, 'r') as f:
                game_state = json.load(f)
            
            if not all(k in game_state for k in ["board", "moves", "time_elapsed"]):
                raise ValueError("invalid save file format.")

            self.stop_timer()
            self.board = game_state["board"]
            self.moves = game_state["moves"]
            self.time_elapsed = game_state["time_elapsed"]
            
            self.moves_label.config(text=f"Moves: {self.moves}")
            self.time_label.config(text=f"Time: {self.time_elapsed}s")
            self.redraw_board()
            self.start_timer()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load game state: {e}")

    def on_closing(self):
        # handles the window closing event gracefully
        self.stop_timer()
        self.root.destroy()

    # helper methods below are mostly unchanged
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        # draws a rectangle with rounded corners on the canvas
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
                  x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def _get_coords(self, r, c):
        # calculates pixel coordinates for a given grid position
        x1 = c * TILE_SIZE + (c + 1) * TILE_PADDING
        y1 = r * TILE_SIZE + (r + 1) * TILE_PADDING
        x2 = x1 + TILE_SIZE
        y2 = y1 + TILE_SIZE
        return x1, y1, x2, y2
    
    def new_game(self):
        # sets up a new puzzle
        self.generate_puzzle(difficulty_moves=50)
        self.redraw_board()
        self.reset_stats()
        self.stop_timer()
        self.is_animating = False

    def _canvas_click_handler(self, event):
        # handles clicks on the game board canvas
        if self.is_animating: return
        col = int(event.x // (TILE_SIZE + TILE_PADDING))
        row = int(event.y // (TILE_SIZE + TILE_PADDING))
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            self.move_tile(row, col)
    
    def _animate_tile_slide(self, item_ids, from_pos, to_pos, on_finish_callback):
        # smoothly animates a tile sliding from one spot to another
        rect_id, shadow_id, text_id = item_ids
        from_r, from_c = from_pos
        to_r, to_c = to_pos
        start_x, start_y, _, _ = self._get_coords(from_r, from_c)
        end_x, end_y, _, _ = self._get_coords(to_r, to_c)
        dx, dy = end_x - start_x, end_y - start_y
        num_steps = 15
        step_x, step_y = dx / num_steps, dy / num_steps

        def _step(current_step):
            if current_step <= num_steps:
                for item_id in item_ids:
                    self.canvas.move(item_id, step_x, step_y)
                self.root.after(8, lambda: _step(current_step + 1))
            else:
                on_finish_callback()
        _step(1)
    
    def reset_stats(self):
        # resets moves and timer
        self.moves, self.time_elapsed = 0, 0
        self.timer_running = False
        self.moves_label.config(text="Moves: 0")
        self.time_label.config(text="Time: 0s")

    def stop_timer(self): self.timer_running = False
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def check_win(self): return self.board == GOAL_STATE
    def find_blank(self, board):
        for r, row in enumerate(board):
            for c, val in enumerate(row):
                if val == EMPTY_TILE: return r, c
        return None
    
    def _get_neighbors(self, board):
        # finds all valid moves from a given board state
        neighbors = []
        i, j = self.find_blank(board)
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                new_state = copy.deepcopy(board)
                new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
                neighbors.append(new_state)
        return neighbors

    def board_to_tuple(self, board): return tuple(num for row in board for num in row)
    def manhattan_distance(self, board):
        # heuristic: sum of distances of each tile from its goal position
        distance = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                val = board[i][j]
                if val != EMPTY_TILE:
                    goal_i, goal_j = divmod(val - 1, BOARD_SIZE)
                    distance += abs(goal_i - i) + abs(goal_j - j)
        return distance

    def misplaced_tiles(self, board):
        # heuristic: counts the number of tiles not in their correct spot
        misplaced = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] != EMPTY_TILE and board[i][j] != GOAL_STATE[i][j]:
                    misplaced += 1
        return misplaced
    
    def generate_puzzle(self, difficulty_moves=50):
        # creates a solvable puzzle by making random moves from the goal state
        self.board = copy.deepcopy(GOAL_STATE)
        last_move = None
        for _ in range(difficulty_moves):
            blank_i, blank_j = self.find_blank(self.board)
            possible_moves = []
            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = blank_i + di, blank_j + dj
                if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and (ni, nj) != last_move:
                    possible_moves.append((ni, nj))
            if not possible_moves: continue
            move_i, move_j = random.choice(possible_moves)
            self.board[blank_i][blank_j], self.board[move_i][move_j] = self.board[move_i][move_j], self.board[blank_i][blank_j]
            last_move = (blank_i, blank_j)

    def _solve_bfs(self):
        # breadth-first search, now returns path and performance stats
        nodes_expanded = 0
        start_node = self.board
        queue = deque([(start_node, [])])
        visited = {self.board_to_tuple(start_node)}

        while queue:
            current_board, path = queue.popleft()
            nodes_expanded += 1
            if current_board == GOAL_STATE:
                return path, {"nodes_expanded": nodes_expanded}

            for neighbor in self._get_neighbors(current_board):
                if self.board_to_tuple(neighbor) not in visited:
                    visited.add(self.board_to_tuple(neighbor))
                    queue.append((neighbor, path + [neighbor]))
        return None, {"nodes_expanded": nodes_expanded}

def main():
    root = tk.Tk()
    game = PuzzleGUI(root)
    # this try/except block handles ctrl+c in the terminal
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nprogram closed by user.")
        game.on_closing()

if __name__ == "__main__":
    main()

