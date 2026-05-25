# A* Pac-Man Maze Solver

A Python-based Pac-Man pathfinding simulation powered by the **A* Search algorithm** and visualized using **Pygame**. 

Pac-Man navigates a customizable maze, searching for the optimal path to consume all food items while utilizing unique mechanics such as corner teleportation and wall-passing power-ups.

---

## 🚀 Key Features

*   **A\* Pathfinding Algorithm:** Finds the optimal route to collect all food pellets scattered across the grid.
*   **Custom Heuristic Function:** Leverages Manhattan distance to the closest food item for efficient search space pruning.
*   **Wall-Pass Power-up (Pie):** Collecting a green Pie (`O`) grants Pac-Man a temporary ability (5 steps) to move through solid walls.
*   **Corner Teleportation:** Stepping onto corner tiles teleports Pac-Man to the opposite corner of the map.
*   **Pygame Visualization:** Smooth step-by-step path animation with retro sound effects for food collection and power-ups.
*   **Custom Map Support:** Easily design and load grid layouts from standard text files.

---

## 🛠️ Tech Stack & Dependencies

*   **Language:** Python 3.x
*   **GUI & Audio:** Pygame
*   **Data Structures:** Heapq (Min-priority queue for A\* frontier)

---

## 🎮 How to Run

1.  **Install dependencies:**
    ```bash
    pip install pygame
    ```

2.  **Run the simulation:**
    Pass the path of the layout file as a command-line argument:
    ```bash
    python main.py map.txt
    ```

---

## 🗺️ Map Legend
*   `P` : Pac-Man starting position
*   `%` : Wall
*   `.` : Food
*   `O` : Pie (Wall-pass power-up)

---
*Created by Eddy.*
