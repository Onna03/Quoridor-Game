# Quoridor AI

> A visually immersive, high-performance Python implementation of the abstract strategy game **Quoridor**. This project features a robust **Minimax AI**, a glowing **Cyberpunk UI**, and advanced gameplay features like **Undo/Redo** and **Pathfinding Validation**.

---

## Features

- **Intelligent AI:** A competitive computer opponent powered by **Minimax with Alpha-Beta Pruning**.
- **Neon Aesthetics:** A polished Cyberpunk visual theme with glowing effects and smooth UI scaling.
- **Time Travel:** Full **Undo/Redo** support (`Ctrl+Z` / `Ctrl+Y`) to fix mistakes or analyze moves.
- **Fair Play Engine:** Real-time **BFS Pathfinding** that strictly enforces valid wall placements (no blocking opponents completely).
- **Dual Modes:** Play locally against a friend (PvP) or challenge the AI (PvE).

---

## Repository Layout

```text

├── Board.py         # Main board logic and game state

├── Player.py        # Player logic (movement, validation)

├── AIPlayer.py      # (Expected) AI behavior for Player 2

├── README.md        # Project documentation

```

---

## Controls

| Action            | Input Key / Mouse                                                      |
| ----------------- | ---------------------------------------------------------------------- |
| **Move Pawn**     | `Arrow Keys` (Up, Down, Left, Right)                                   |
| **Diagonal Jump** | `Q` (Top-Left), `E` (Top-Right), `Z` (Bottom-Left), `C` (Bottom-Right) |
| **Place Wall**    | **Left Click** on the gap between cells                                |
| **Undo Move**     | `Ctrl` + `Z`                                                           |
| **Redo Move**     | `Ctrl` + `Y`                                                           |
| **Exit Game**     | Click the **EXIT** button on the Winner screen                         |

---

## Installation & Run

1. **Clone the Repository:**

```bash
git clone https://github.com/YourUsername/Quoridor-Neon.git
cd Quoridor-Neon

```

2. **Install Dependencies:**

```bash
pip install pygame numpy

```

3. **Launch the Game:**

```bash
python main.py

```

---

## AI Strategy (How it thinks)

The AI uses a **Minimax algorithm** optimized with **Alpha-Beta Pruning** to look ahead several turns. It evaluates board states based on:

1. **Path Efficiency:** The difference in shortest path length (A\*) between itself and the opponent.
2. **Wall Advantage:** The number of walls remaining compared to the opponent.
3. **Winning Potential:** Immediate priority is given to winning moves or blocking an opponent's win.

---

## Implementation Details

### The Undo/Redo System

To ensure stability, the game uses a **Deep Copy Snapshot** system.

- **Before every move**, the entire board state (grid, positions, walls) is cloned and pushed to a `History Stack`.
- **Undoing** pops the state and pushes it to a `Redo Stack`.
- **Making a new move** clears the `Redo Stack` to prevent timeline corruption.

### The Coordinate System

The board uses an internal **17x17 Grid** to represent a logical 9x9 board.

- **Even indices (0, 2, 4...)** represent **Cells** (where pawns stand).
- **Odd indices (1, 3, 5...)** represent **Gaps** (where walls are placed).
  This hybrid approach simplifies the logic for checking wall collisions and pathfinding.

---
