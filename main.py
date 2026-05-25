import pygame as pg
import constants as cs
import sys
import heapq
from models.pacman import Pacman
from models.food import Food
from models.wall import Wall
from models.pie import Pie
import time


class Frontier():
    def __init__(self, f, state, g=0, path=[]):
        self.f = f
        self.g = g
        self.state = state
        self.path = path

    def __lt__(self, other):
        if self.f != other.f:
            return self.f < other.f
        # If f-values are equal, prefer the node with lower g (shorter path so far)
        return self.g < other.g


class State:
    def __init__(
            self, 
            pacman_pos, 
            food_points, 
            direction = "",
            wall_pass_steps=0
    ):
        self.pacman_pos = pacman_pos  # (x, y) tuple
        self.food_points = frozenset(food_points)  # Set of (x, y) tuples for food
        self.direction = direction
        self.wall_pass_steps = wall_pass_steps  # Number of wall-pass steps remaining

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.pacman_pos == other.pacman_pos and
                self.food_points == other.food_points and
                self.wall_pass_steps == other.wall_pass_steps and
                self.direction == other.direction)

    def __hash__(self):
        return hash((
            self.pacman_pos, 
            self.food_points, 
            self.wall_pass_steps, 
            self.direction
        ))


'''
    This class will load the map, the pacman, the foods and walls
    It also handles all the logic related to A*, heuristic function
'''
class MazeGame():
    def __init__(self, layout_file):
        self.layout_file = layout_file
        self.pacman_pos = 0
        self.food_points = list()
        self.pie_points = list()
        self.wall_points = list()
        self.width = 0
        self.height = 0
        self.load_map()
        
    def load_map(self):
        with open(self.layout_file, "r") as file:
            lines = [line.strip() for line in file.readlines()]
            self.height = len(lines)
            self.width = max(len(line) for line in lines) if lines else 0

            for y, line in enumerate(lines):
                for x, char in enumerate(line):
                    if char == '%':
                        self.wall_points.append((x, y))
                    elif char == '.':
                        self.food_points.append((x, y))
                    elif char == 'P':
                        self.pacman_pos = (x, y)
                    elif char == 'O':
                        self.pie_points.append((x, y))

    def is_valid_move(self, position: tuple):
        x, y = position
        return (0 <= x < self.width and 0 <= y < self.height) \
                and position not in self.wall_points

    def is_at_corner(self, position: tuple):
        return position in [
            (0, 0), 
            (0, self.width - 1), 
            (self.height - 1, 0),
            (self.height - 1, self.width - 1) 
        ]
        
    def teleport(self, position: tuple):
        new_x, new_y = 0, 0

        if position == (0,0):
            # Top-left corner -> bottom-right
            new_x, new_y = self.width - 1, self.height - 1
        elif position == (0, self.width - 1):
            # Top-right corner -> bottom-left
            new_x, new_y = 0, self.height - 1
        elif position == (self.width - 1, self.height - 1):
            # Bottom-right corner -> top-left
            new_x, new_y = 0, 0
        elif position == (0, self.height - 1):
            # Bottom-left corner -> top-right
            new_x, new_y = self.width - 1, 0

        return (new_x, new_y)
    
    # This method is to find successors of the current state (pacman)
    def get_successors(self, state):
        successors = []
        directions = [
            ("North", (0, -1)),
            ("South", (0, 1)),
            ("West", (-1, 0)),
            ("East", (1, 0))
        ]
        cur_x, cur_y = state.pacman_pos

        for direction, (dx, dy) in directions:
            new_pos = (cur_x + dx, cur_y + dy)
            if self.is_at_corner(new_pos):
                new_pos = self.teleport(new_pos)

            if not self.is_valid_move(new_pos) and state.wall_pass_steps <= 0:
                continue

            new_food_points = set(state.food_points)
            if new_pos in new_food_points:
                new_food_points.remove(new_pos)

            new_wall_pass_steps = max(0, state.wall_pass_steps - 1)
            if new_pos in self.pie_points:
                new_wall_pass_steps = 5

            successors.append(
                State(
                    pacman_pos = new_pos,
                    food_points = new_food_points, 
                    wall_pass_steps = new_wall_pass_steps,
                    direction = direction
                ))

        return successors
    
    # Calculate distance from the current position of pacman to the goal
    def heuristic(self, state):
        if not state.food_points:
            return 0
        px, py = state.pacman_pos
        min_dist = float('inf')
        for fx, fy in state.food_points:
            dist = abs(px - fx) + abs(py - fy)
            min_dist = min(min_dist, dist)
        return min_dist

    def implement_a_star(self):
        init_state = State(self.pacman_pos, self.food_points, 0)
        frontier = [
            Frontier(
                f = self.heuristic(init_state), 
                state=init_state
            )
        ]
        visited = {}  # Map state to best g value

        while frontier:
            temp_frontier = heapq.heappop(frontier)
            state = temp_frontier.state

            if state in visited and visited[state] <= temp_frontier.g:
                continue
            visited[state] = temp_frontier.g

            if not state.food_points:  # Goal: all food collected
                return temp_frontier.path, temp_frontier.g

            for child in self.get_successors(state):
                new_g = temp_frontier.g + 1
                heapq.heappush(
                    frontier, 
                    Frontier(
                        f = new_g + self.heuristic(child), 
                        g = new_g, 
                        state = child, 
                        path = temp_frontier.path + [child.direction]
                    )
                )

        return [], 0  # No path found

'''
    This class will handle the game's animation
    so that the game would run lively
'''

class Visualizer:
    def __init__(self, maze, path):
        self.maze = maze
        self.path = path
        self.cell_size = cs.SPRITE_SIZE  # Size of each cell in pixels
        self.width = maze.width * self.cell_size
        self.height = maze.height * self.cell_size
        self.screen = None
        self.pacman = None
        self.eat_food_sound = None
        self.eat_pie_sound = None
        self.clock = None
        self.fps = 5
        self.food_sprites = pg.sprite.Group()
        self.pie_sprites = pg.sprite.Group()
        self.wall_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

    def initialize(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Pac-Man Game")
        self.screen.fill(cs.BG_COLOR) 
        self.eat_food_sound = pg.mixer.Sound(cs.EAT_FOOD_SOUND_URL)
        self.eat_pie_sound = pg.mixer.Sound(cs.EAT_PIE_SOUND_URL)
        self.clock = pg.time.Clock()

        # Create Pac-Man sprite
        self.pacman = Pacman(
            x = self.maze.pacman_pos[0], 
            y = self.maze.pacman_pos[1], 
            size = self.cell_size
        )
        self.all_sprites.add(self.pacman)

        # Create food sprites
        for x, y in self.maze.food_points:
            food = Food(x, y, self.cell_size)
            self.food_sprites.add(food)
            self.all_sprites.add(food)

        # Create pie sprites
        for x, y in self.maze.pie_points:
            pie = Pie(x, y, self.cell_size)
            self.pie_sprites.add(pie)
            self.all_sprites.add(pie)

        # Create wall sprites
        for x, y in self.maze.wall_points:
            wall = Wall(x, y, self.cell_size)
            self.wall_sprites.add(wall)
            self.all_sprites.add(wall)

    def draw(self):
        self.screen.fill(cs.BG_COLOR)  # Clear the screen
        self.all_sprites.draw(self.screen)
        pg.display.flip()
        self.clock.tick(self.fps)


    def visualize(self):
        if not self.maze: return
            
        self.initialize()
        pacman_pos = self.maze.pacman_pos
        wall_pass_steps = 0
        food_collected = 0
        total_food = len(self.food_sprites)

         # Draw initial state
        self.draw()

        # Animate each step
        for direction in self.path:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # Update Pac-Man's position
            dx, dy = {
                "North": (0, -1),
                "South": (0, 1),
                "West": (-1, 0),
                "East": (1, 0)
            }[direction]
            new_pos = (pacman_pos[0] + dx, pacman_pos[1] + dy)

            if self.maze.is_at_corner(new_pos):
                new_pos = self.maze.teleport(new_pos)

            # Check for collisions with food
            food_collisions = pg.sprite.spritecollide(
                self.pacman, self.food_sprites, dokill=True
            )
            if food_collisions:
                food_collected += len(food_collisions)
                self.eat_food_sound.play()
                print(f"Collected {len(food_collisions)} food item. Total collected: {food_collected}/{total_food}")

            # Check for collisions with pie
            pie_collisions = pg.sprite.spritecollide(
                self.pacman, self.pie_sprites, dokill=True
            )
            if pie_collisions:
                wall_pass_steps = 5
                self.eat_pie_sound.play()
                print(f"Power upp! Passing walls with steps: {wall_pass_steps}")

            # Update wall-pass steps
            wall_pass_steps = max(0, wall_pass_steps - 1)

            # Update Pac-Man's position
            pacman_pos = new_pos
            self.pacman.update(pacman_pos[0], pacman_pos[1])
            self.draw()

        # Keep the window open until closed
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()


def main(layout_file):
    # Create a maze
    maze = MazeGame(layout_file = layout_file)
    path, cost = maze.implement_a_star()
    visualizer = Visualizer(maze, path)
    visualizer.visualize()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python <your_main_file>.py <layout_file>")
        sys.exit(1)
    main(sys.argv[1])










































































































# made by Eddy with heart