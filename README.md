# ♟️ Quoridor AI & Game Engine

> A modular Python implementation of the classic strategy board game **Quoridor**. This project features a robust game engine supporting Human vs. Human and Human vs. AI modes, built with object-oriented principles and pathfinding validation.

---

## 📂 Repository Layout

```text

├── Board.py         # Main board logic and game state

├── Player.py        # Player logic (movement, validation)

├── AIPlayer.py      # (Expected) AI behavior for Player 2

├── README.md        # Project documentation

```

---

## 🎯 Gameplay Mechanics

The engine implements the standard Quoridor ruleset on a `9x9` logical grid (mapped internally to a `17x17` matrix to account for wall spaces).

### Key Rules

* **Objective:** The first player to reach any cell on the opposing baseline wins.
* **Turn Actions:** Choose between moving your pawn or placing a wall.
* **Wall Logic:** Walls block movement but **cannot** completely seal off a player's path to the goal.
* **Advanced Movement:** Supports orthogonal moves and diagonal jumps (if an opponent blocks the forward path).

---

## 🏗️ Architecture & Classes

### 1. The Board (`Board.py`)

The central controller for the match. It maintains the master state using a `numpy` 2D array.

* **Grid System:**
* `dimPawnBoard`: **9** (Playable cells)
* `dimBoard`: **17** (Total matrix size including wall slots)


* **Methods:**
* `__init__(dim, againest_ai)`: Sets up the board and spawns `Player` or `AIPlayer` instances.
* `get_state()`: Exports the current board configuration for the UI or AI analysis.



### 2. The Player (`Player.py`)

Handles individual entity state and legal move generation.

* **State Tracking:** Tracks `id` (1 vs 2), current `pos` (coordinates), and `available_walls` inventory.
* **Movement Logic:**
* `checkDirection()` & `checkDiagonalDirection()`: Validates standard and complex moves.
* `move()`: Executes the verified move logic.


* **Fair Play Validation:**
* **BFS Pathfinding:** Uses `WallRestrictionAlgorithmsBFS(new_board)` to simulate wall placement. If a wall makes the goal unreachable for *any* player, the move is rejected.



---

## 🚀 Getting Started

### Prerequisites

* Python 3.x
* NumPy

### Installation

**1. Clone the project**

```bash
git clone https://github.com/your-username/Quoridor-Game-AI-Project.git
cd Quoridor-Game-AI-Project

```

**2. Install requirements**

```bash
pip install numpy

```

**3. Launch the engine**

```bash
python main.py

```

---

## 🗺️ Roadmap

* [ ] **AI Development:** Finalize heuristics and decision trees in `AIPlayer.py`.
* [ ] **Interface:** Build a visual frontend using **Pygame** or **Tkinter**.
* [ ] **Interaction:** Add a CLI or GUI loop for wall placement.
* [ ] **Refinement:** Optimize the BFS validation for deeper search trees.