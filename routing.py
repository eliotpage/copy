# routing.py

import math
from storage import Storage

class DStarLite:
    """
    Simplified grid-based pathfinding (A* used as PoC).
    Integrates obstacles from storage.
    """

    def __init__(self, storage: Storage, width, height, default_cost=1):
        self.storage = storage
        self.width = width
        self.height = height
        self.default_cost = default_cost

        self.cost_map = {}
        for x in range(width):
            for y in range(height):
                self.cost_map[(x, y)] = default_cost

        self.start = None
        self.goal = None
        self.path = []

        self.update_obstacles()
        print(f"[Routing] Initialized grid {width}x{height}")

    def update_obstacles(self):
        obstacles = self.storage.get_all_obstacles()
        for obs in obstacles:
            x0, y0 = self.latlon_to_grid(obs['lat'], obs['lon'])
            radius = obs.get('radius', 1.0)
            for x in range(self.width):
                for y in range(self.height):
                    if self.distance((x0, y0), (x, y)) <= radius:
                        self.cost_map[(x, y)] = float('inf')
        print(f"[Routing] Obstacles updated, {len(obstacles)} loaded")

    def latlon_to_grid(self, lat, lon):
        gx = int(lat * (self.width / 180))
        gy = int(lon * (self.height / 360))
        gx = max(0, min(self.width - 1, gx))
        gy = max(0, min(self.height - 1, gy))
        return gx, gy

    def distance(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def cost(self, node):
        return self.cost_map.get(node, self.default_cost)

    def heuristic(self, a, b):
        return self.distance(a, b)

    def find_path(self, start_latlon, goal_latlon):
        self.start = self.latlon_to_grid(*start_latlon)
        self.goal = self.latlon_to_grid(*goal_latlon)
        self.update_obstacles()

        import heapq
        open_set = []
        heapq.heappush(open_set, (0, self.start))
        came_from = {}
        g_score = {self.start: 0}
        f_score = {self.start: self.heuristic(self.start, self.goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == self.goal:
                path = self.reconstruct_path(came_from, current)
                print(f"[Routing] Path found with {len(path)} nodes")
                return path

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + self.cost(neighbor)
                if tentative_g >= float('inf'):
                    continue
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        print("[Routing] No path found")
        return []

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        self.path = path
        return path
