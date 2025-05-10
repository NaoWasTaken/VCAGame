import pygame
import heapq

ENEMY_DEFAULT_COLOR = (255, 0, 0)
STUN_OUTLINE_COLOR = (0, 0, 255)
OUTLINE_THICKNESS = 2
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_Y_OFFSET = 8

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __hash__(self):
        return hash(self.position)

def astar_pathfind(dungeon_tiles, tile_size, start_pixel, end_pixel, character_width_tiles=1):
    start_node_pos = (int(start_pixel[0] // tile_size), int(start_pixel[1] // tile_size))
    end_node_pos = (int(end_pixel[0] // tile_size), int(end_pixel[1] // tile_size))

    start_node = Node(None, start_node_pos)

    open_list_heap = []
    node_counter = 0

    open_nodes_map = {}

    closed_set = set()

    start_node.g = 0
    start_node.h = abs(start_node.position[0] - end_node_pos[0]) + abs(start_node.position[1] - end_node_pos[1])
    start_node.f = start_node.g + start_node.h

    heapq.heappush(open_list_heap, (start_node.f, node_counter, start_node))
    node_counter += 1
    open_nodes_map[start_node.position] = start_node

    map_width_tiles = len(dungeon_tiles[0])
    map_height_tiles = len(dungeon_tiles)

    neighbor_moves = [
        (0, -1, 1), (0, 1, 1), (-1, 0, 1), (1, 0, 1),
        (-1, -1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, 1)
    ]


    while len(open_list_heap) > 0:
        current_f, _, current_node = heapq.heappop(open_list_heap)

        if current_node.position not in open_nodes_map or \
           open_nodes_map[current_node.position].f < current_f:
            continue

        if current_node.position == end_node_pos:
            path = []
            temp_current = current_node
            while temp_current is not None:
                path.append(temp_current.position)
                temp_current = temp_current.parent
            return path[::-1]

        closed_set.add(current_node.position)
        if current_node.position in open_nodes_map:
            del open_nodes_map[current_node.position]


        for move_x, move_y, move_cost in neighbor_moves:
            neighbor_pos = (current_node.position[0] + move_x, current_node.position[1] + move_y)

            if not (0 <= neighbor_pos[0] < map_width_tiles and 0 <= neighbor_pos[1] < map_height_tiles):
                continue

            if dungeon_tiles[neighbor_pos[1]][neighbor_pos[0]] != 1:  # 1 is floor/walkable
                continue

            if neighbor_pos in closed_set:
                continue

            if abs(move_x) == 1 and abs(move_y) == 1:
                wall_check_pos1_x = current_node.position[0] + move_x
                wall_check_pos1_y = current_node.position[1]
                wall_check_pos2_x = current_node.position[0]
                wall_check_pos2_y = current_node.position[1] + move_y

                if dungeon_tiles[wall_check_pos1_y][wall_check_pos1_x] == 0 and \
                   dungeon_tiles[wall_check_pos2_y][wall_check_pos2_x] == 0:
                    continue

            tentative_g = current_node.g + move_cost

            existing_neighbor_node_in_open = open_nodes_map.get(neighbor_pos)
            if existing_neighbor_node_in_open is not None and tentative_g >= existing_neighbor_node_in_open.g:
                continue

            neighbor_node = existing_neighbor_node_in_open if existing_neighbor_node_in_open else Node(position=neighbor_pos)
            neighbor_node.parent = current_node
            neighbor_node.g = tentative_g
            neighbor_node.h = abs(neighbor_pos[0] - end_node_pos[0]) + abs(neighbor_pos[1] - end_node_pos[1]) # Manhattan
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            heapq.heappush(open_list_heap, (neighbor_node.f, node_counter, neighbor_node))
            node_counter += 1
            open_nodes_map[neighbor_pos] = neighbor_node

    return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_id, width=30, height=30, health=50, speed=1.5, damage=10):
        super().__init__()

        self.id = enemy_id
        self.name = f"Enemy_{self.id}"

        self.width = width
        self.height = height

        self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.original_image.fill(ENEMY_DEFAULT_COLOR)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pixel_pos = pygame.math.Vector2(self.rect.topleft)

        self.health = health
        self.max_health = health
        self.speed = float(speed)
        self.damage = damage
        self.alive = True

        self.stun_timer = 0
        self.is_stunned_by_lightning_visual = False

        self.path = []
        self.path_recalculation_interval = 30
        self.path_recalculation_timer = self.path_recalculation_interval
        self.current_path_target_tile = None
        self.current_pixel_target = None
        self.player_last_known_tile = None

        self.stuck_timer = 0
        self.max_stuck_time = 5

    def apply_stun(self, duration_frames, is_lightning_stun=False):
        if not self.alive:
            return
        self.stun_timer = max(self.stun_timer, duration_frames)
        if is_lightning_stun:
            self.is_stunned_by_lightning_visual = True
            self._apply_stun_visual()

    def _apply_stun_visual(self):
        if not self.is_stunned_by_lightning_visual:
             return

        outlined_image_width = self.width + OUTLINE_THICKNESS * 2
        outlined_image_height = self.height + OUTLINE_THICKNESS * 2
        new_image = pygame.Surface((outlined_image_width, outlined_image_height), pygame.SRCALPHA)
        new_image.blit(self.original_image, (OUTLINE_THICKNESS, OUTLINE_THICKNESS))
        pygame.draw.rect(new_image, STUN_OUTLINE_COLOR, new_image.get_rect(), OUTLINE_THICKNESS)
        self.image = new_image
        current_center = self.rect.center
        self.rect = self.image.get_rect(center=current_center)
        self.pixel_pos.update(self.rect.topleft)


    def _remove_stun_visual(self):
        if self.image is not self.original_image:
            self.image = self.original_image.copy()
            current_center = self.rect.center
            self.rect = self.image.get_rect(center=current_center)
            self.pixel_pos.update(self.rect.topleft)
        self.is_stunned_by_lightning_visual = False


    def update(self, player, dungeon, all_enemies_list):
        if not self.alive:
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                self._remove_stun_visual()
            return

        self.path_recalculation_timer -= 1
        player_current_tile = (int(player.rect.centerx // dungeon.tile_size),
                               int(player.rect.centery // dungeon.tile_size))

        needs_new_path = False
        if not self.path:
            needs_new_path = True
        elif player_current_tile != self.player_last_known_tile:
            needs_new_path = True
        elif self.path_recalculation_timer <= 0:
            needs_new_path = True
        elif not self.current_path_target_tile:
            needs_new_path = True


        if needs_new_path:
            self.path_recalculation_timer = self.path_recalculation_interval
            self.player_last_known_tile = player_current_tile

            new_path_tiles = astar_pathfind(dungeon.tiles, dungeon.tile_size, self.rect.center, player.rect.center)

            if new_path_tiles and len(new_path_tiles) > 0:
                self.path = new_path_tiles
                if len(self.path) > 1 and self.path[0] == (self.rect.centerx // dungeon.tile_size, self.rect.centery // dungeon.tile_size):
                    self.path.pop(0)

                if self.path:
                    self.current_path_target_tile = self.path[0]
                    self.current_pixel_target = pygame.math.Vector2(
                        self.current_path_target_tile[0] * dungeon.tile_size + dungeon.tile_size // 2,
                        self.current_path_target_tile[1] * dungeon.tile_size + dungeon.tile_size // 2
                    )
                    self.stuck_timer = 0
                else:
                    self.current_path_target_tile = None
                    self.current_pixel_target = None
            else:
                self.path = []
                self.current_path_target_tile = None
                self.current_pixel_target = None

        move_vector = pygame.math.Vector2(0, 0)
        original_pixel_pos = self.pixel_pos.copy()

        if self.current_pixel_target and self.path:
            direction_to_target = self.current_pixel_target - pygame.math.Vector2(self.rect.centerx, self.rect.centery)
            distance_to_target = direction_to_target.length()

            if distance_to_target > 1:
                actual_move_distance = min(self.speed, distance_to_target)
                move_vector = direction_to_target.normalize() * actual_move_distance

                if distance_to_target <= self.speed:
                    self.pixel_pos = self.current_pixel_target.copy()
                    self.rect.center = (round(self.pixel_pos.x), round(self.pixel_pos.y))
                    move_vector.update(0,0)

                    self.path.pop(0)
                    if self.path:
                        self.current_path_target_tile = self.path[0]
                        self.current_pixel_target = pygame.math.Vector2(
                            self.current_path_target_tile[0] * dungeon.tile_size + dungeon.tile_size // 2,
                            self.current_path_target_tile[1] * dungeon.tile_size + dungeon.tile_size // 2
                        )
                        self.stuck_timer = 0
                    else:
                        self.current_path_target_tile = None
                        self.current_pixel_target = None
            else: 
                self.path.pop(0)
                if self.path:
                    self.current_path_target_tile = self.path[0]
                    self.current_pixel_target = pygame.math.Vector2(
                        self.current_path_target_tile[0] * dungeon.tile_size + dungeon.tile_size // 2,
                        self.current_path_target_tile[1] * dungeon.tile_size + dungeon.tile_size // 2
                    )
                    self.stuck_timer = 0
                else:
                    self.current_path_target_tile = None
                    self.current_pixel_target = None
        else:
            direction_to_player = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
            distance_to_player = direction_to_player.length()
            attack_range = dungeon.tile_size * 0.8

            if distance_to_player > attack_range and distance_to_player > 0:
                move_vector = direction_to_player.normalize() * self.speed * 0.5

        if move_vector.length_squared() > 0:
            prev_rect_x = self.rect.x
            prev_rect_y = self.rect.y

            self.pixel_pos.x += move_vector.x
            self.rect.x = round(self.pixel_pos.x)
            if self.check_collision_against_walls(dungeon) or \
               self.check_collision_against_enemies(all_enemies_list, self):
                self.pixel_pos.x = float(prev_rect_x)
                self.rect.x = prev_rect_x
                move_vector.x = 0

            self.pixel_pos.y += move_vector.y
            self.rect.y = round(self.pixel_pos.y)
            if self.check_collision_against_walls(dungeon) or \
               self.check_collision_against_enemies(all_enemies_list, self):
                self.pixel_pos.y = float(prev_rect_y)
                self.rect.y = prev_rect_y
                move_vector.y = 0

        current_center_pos = pygame.math.Vector2(self.rect.center)
        intended_movement = (original_pixel_pos != self.pixel_pos)

        if intended_movement and pygame.math.Vector2(original_pixel_pos).distance_to(self.pixel_pos) < 0.1:
            self.stuck_timer += 1
            if self.stuck_timer > self.max_stuck_time:
                self.path = []
                self.current_path_target_tile = None
                self.current_pixel_target = None
                self.stuck_timer = 0
        elif intended_movement:
             self.stuck_timer = 0


    def check_collision_against_walls(self, dungeon):
        collision_rect = self.rect

        min_tx = int(collision_rect.left // dungeon.tile_size)
        max_tx = int(collision_rect.right // dungeon.tile_size)
        min_ty = int(collision_rect.top // dungeon.tile_size)
        max_ty = int(collision_rect.bottom // dungeon.tile_size)

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if 0 <= ty < dungeon.height_tiles and 0 <= tx < dungeon.width_tiles:
                    if dungeon.tiles[ty][tx] == 0:
                        wall_rect = pygame.Rect(tx * dungeon.tile_size, ty * dungeon.tile_size,
                                                dungeon.tile_size, dungeon.tile_size)
                        if collision_rect.colliderect(wall_rect):
                            return True
        return False

    def check_collision_against_enemies(self, all_enemies_list, current_enemy_skip):
        for other_enemy in all_enemies_list:
            if other_enemy is not current_enemy_skip and other_enemy.alive:
                if self.rect.colliderect(other_enemy.rect):
                    return True
        return False

    def take_damage(self, amount):
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.kill()

    def draw(self, surface):
        if self.alive:
            self.rect.topleft = (round(self.pixel_pos.x), round(self.pixel_pos.y))
            surface.blit(self.image, self.rect)

            if self.health < self.max_health and self.health > 0:
                bar_full_width = self.rect.width
                bar_current_width = int(bar_full_width * (self.health / self.max_health))
                bar_pos_x = self.rect.left
                bar_pos_y = self.rect.top - HEALTH_BAR_Y_OFFSET - HEALTH_BAR_HEIGHT

                pygame.draw.rect(surface, (100, 0, 0),
                                 (bar_pos_x, bar_pos_y, bar_full_width, HEALTH_BAR_HEIGHT))
                if bar_current_width > 0:
                    pygame.draw.rect(surface, (0, 200, 0),
                                     (bar_pos_x, bar_pos_y, bar_current_width, HEALTH_BAR_HEIGHT))
            
            # --- DEBUG: Add this if you want to see the pathing Vi :3 SIKE
            # if self.path:
            #     path_points = []
            #     path_points.append(self.rect.center)
            #     for tile_pos in self.path:
            #         pixel_x = tile_pos[0] * dungeon.tile_size + dungeon.tile_size // 2
            #         pixel_y = tile_pos[1] * dungeon.tile_size + dungeon.tile_size // 2
            #         path_points.append((pixel_x, pixel_y))
                
            #     if len(path_points) > 1:
            #         pygame.draw.lines(surface, (0, 255, 255, 100), False, path_points, 1)
            
            # if self.current_pixel_target:
            #     pygame.draw.circle(surface, (255, 255, 0), (int(self.current_pixel_target.x), int(self.current_pixel_target.y)), 3)