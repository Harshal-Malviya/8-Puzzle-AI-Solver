# 8-Puzzle AI Pro

Hey there! Welcome to my 8-Puzzle AI project. I built this to dive deep into classic AI search algorithms and create a really polished, interactive experience using just Python and its built-in GUI library, tkinter.



## ✨ What Can It Do?

This is more than just a simple game. It's a fun sandbox for watching different AI strategies work in real-time.

* **Modern, Animated UI**:
    * Every move, whether yours or the AI's, has a smooth sliding animation.
    * The whole look is inspired by Material Design 3 (Google), with a clean color palette and rounded corners.
    * Tiles and buttons have a subtle "lifted" look and react when you hover over them.
* **AI Solvers**:
    * **A\* Search**: The smart, "informed" algorithm. You can pick between two powerful ways for it to "think":
        * **Manhattan Distance:** The most efficient heuristic for this kind of puzzle.
        * **Misplaced Tiles:** A simpler heuristic, fun to compare against.
    * **Breadth-First Search (BFS)**: The classic "uninformed" approach. It's guaranteed to find the shortest solution, but it has to work a lot harder to get there!
* **See How the AI Thinks**:
    * When the AI finishes, you get a cool analytics report showing:
        * How many moves it took.
        * How many different board states it had to check.
        * How fast it found the solution (usually in milliseconds!).
* **Handy Tools & Extras**:
    * **Hint Button**: Stuck? Get a visual cue for the next best move.
    * **Save & Load**: Save a tricky puzzle and come back to it later.
    * **Sound Effects**: Optional clicks and chimes make playing more satisfying.

## 🛠️ Tech Stack

* **Python 3**
* **tkinter** (for the GUI)
* Python's awesome built-in libraries: `heapq`, `deque`, `json`, `time`, `threading`, `os`.
* **playsound** (for the optional sound effects)

## 🚀 Get It Running

Ready to try it out? Here’s how to get it running on your machine.

1.  **Grab the code from GitHub:**
    ```sh
    git clone [https://github.com/Harshal-Malviya/8-Puzzle-With-AI-Solver](https://github.com/Harshal-Malviya/8-Puzzle-With-AI-Solver)
    cd 8-Puzzle-With-AI-Solver
    ```

2.  **Install the one dependency:**
    There's just one extra library needed for the sound effects.
    ```sh
    pip install playsound==1.2.2
    ```
    

3.  **Want some sound? (Optional):**
    If you want audio, just place three `.wav` files in the same folder as the script:
    * `slide.wav`
    * `tick.wav`
    * `solve.wav`
    If you don't have these, no worries! The game will just run silently.

4.  **Run the script:**
    ```sh
    python 8_puzzle_pro.py
    ```

## 🎮 How to Play

* **To move a tile**: Just click any tile that's next to the empty space.
* **To use the AI**:
    1.  Pick an algorithm from the dropdown menu.
    2.  Hit the "Solve" button and watch it go!
* **For a hint**: Click the "Hint" button, and the best tile to move will flash green.
* **To save or load**: The "Save" and "Load" buttons will open your computer's standard file dialog.
