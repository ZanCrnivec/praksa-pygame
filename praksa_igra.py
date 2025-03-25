import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1980, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Igrca")
clock = pygame.time.Clock()

player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5
dash_speed = 50  # Dash speed
dash_cooldown = 500  # Cooldown time in milliseconds
last_dash_time = 0  # Last time the player dashed
is_dashing = False
dash_direction = (0, 0)  # Direction of the dash

camera_x, camera_y = player_x, player_y

# Thrust variables
sword_thrust = False
thrust_velocity = 0
thrust_distance = 0

# For world sag effect
world_offset_x = 0
world_offset_y = 0

stones = [(random.randint(-2000, 2000), random.randint(-2000, 2000), random.randint(10, 50)) for _ in range(80)]

# Player sword damage
sword_damage = 20

# Enemy Class
class Enemy:
    def __init__(self, x, y, speed, damage, color, size, hp):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.color = color
        self.size = size
        self.hp = hp
        self.knockback = 0

    def move_towards_player(self, player_x, player_y):
        # Calculate the direction vector towards the player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance != 0:
            dx /= distance
            dy /= distance
        
        # Move the enemy towards the player
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Apply knockback effect if any
        if self.knockback > 0:
            self.x += dx * self.knockback
            self.y += dy * self.knockback
            self.knockback = 1  # Reduce knockback over time

    def take_damage(self, damage):
        self.hp -= damage
        self.knockback = 10  # Apply knockback when hit

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x - camera_x + WIDTH // 2), int(self.y - camera_y + HEIGHT // 2)), self.size)

    def is_alive(self):
        return self.hp > 0

# Enemy spawn timer
enemy_spawn_time = 3000  # Time in milliseconds (3 seconds)
last_spawn_time = 0
enemies = []

def spawn_enemy():
    # Randomly spawn enemies at a certain position with random attributes
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    speed = random.uniform(0.5, 3)  # Random speed for the enemy
    damage = random.randint(10, 20)  # Random damage value
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))  # Random color
    size = random.randint(30, 50)  # Random size
    hp = random.randint(50, 100)  # Random HP for the enemy
    
    # Create a new enemy and add it to the list
    enemy = Enemy(x, y, speed, damage, color, size, hp)
    enemies.append(enemy)

def handle_movement(keys):
    global player_x, player_y
    if keys[pygame.K_w]: player_y -= player_speed
    if keys[pygame.K_s]: player_y += player_speed
    if keys[pygame.K_a]: player_x -= player_speed
    if keys[pygame.K_d]: player_x += player_speed

def update_sword(player_draw_x, player_draw_y):
    global sword_thrust, thrust_velocity, thrust_distance

    if sword_thrust:
        thrust_distance += thrust_velocity
        thrust_velocity -= 1.5  # faster deceleration
        if thrust_distance <= 0:
            sword_thrust = False
            thrust_velocity = 0
            thrust_distance = 0

    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.atan2(mouse_x - player_draw_x, mouse_y - player_draw_y)

    sword_surface = pygame.Surface((60, 15), pygame.SRCALPHA)
    sword_surface.fill((255, 255, 255))
    sword_rotated = pygame.transform.rotate(sword_surface, math.degrees(angle + 80))

    sword_rect = sword_rotated.get_rect(
        center=(player_draw_x + math.sin(angle) * (80 + thrust_distance),
                player_draw_y + math.cos(angle) * (80 + thrust_distance))
    )
    screen.blit(sword_rotated, sword_rect.topleft)

    # Check if sword collides with enemies
    sword_rect_center = sword_rect.center
    for enemy in enemies:
        enemy_rect = pygame.Rect(int(enemy.x - camera_x + WIDTH // 2 - enemy.size), int(enemy.y - camera_y + HEIGHT // 2 - enemy.size), enemy.size * 2, enemy.size * 2)
        if sword_rect.colliderect(enemy_rect) and sword_thrust:
            enemy.take_damage(sword_damage)

def draw_stones():
    for stone in stones:
        draw_x = stone[0] - camera_x + WIDTH // 2 + int(world_offset_x)
        draw_y = stone[1] - camera_y + HEIGHT // 2 + int(world_offset_y)
        pygame.draw.circle(screen, (128, 128, 128), (draw_x, draw_y), stone[2])

def draw_player(player_draw_x, player_draw_y):
    pygame.draw.circle(screen, (255, 255, 255), (player_draw_x, player_draw_y), 35)

def handle_events():
    global sword_thrust, thrust_velocity, thrust_distance, running, is_dashing, last_dash_time, dash_direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not sword_thrust:
                sword_thrust = True
                thrust_velocity = 10
                thrust_distance = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Only allow dash if moving (i.e., player is pressing movement keys)
                if any([pygame.key.get_pressed()[pygame.K_w],
                        pygame.key.get_pressed()[pygame.K_s],
                        pygame.key.get_pressed()[pygame.K_a],
                        pygame.key.get_pressed()[pygame.K_d]]):
                    # Check cooldown before dashing
                    current_time = pygame.time.get_ticks()
                    if current_time - last_dash_time >= dash_cooldown:
                        is_dashing = True
                        last_dash_time = current_time

def dash():
    global player_x, player_y, is_dashing, dash_direction
    if is_dashing:
        player_x += dash_direction[0] * dash_speed * 7
        player_y += dash_direction[1] * dash_speed * 7
        is_dashing = False  # Reset dash after one use

# === Main Game Loop ===
running = True
while running:
    screen.fill((26, 36, 33))

    keys = pygame.key.get_pressed()
    handle_movement(keys)

    # Track the direction of movement
    direction_x, direction_y = 0, 0
    if keys[pygame.K_w]: direction_y -= 1
    if keys[pygame.K_s]: direction_y += 1
    if keys[pygame.K_a]: direction_x -= 1
    if keys[pygame.K_d]: direction_x += 1

    # Normalize direction to ensure consistent dash speed
    if direction_x != 0 or direction_y != 0:
        length = math.sqrt(direction_x**2 + direction_y**2)
        dash_direction = (direction_x / length, direction_y / length)

    # Dash if space is pressed and the player is moving
    dash()

    # Spawn enemies every 3 seconds
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= enemy_spawn_time:
        spawn_enemy()
        last_spawn_time = current_time

    # Update and draw enemies
    for enemy in enemies:
        enemy.move_towards_player(player_x, player_y)
        enemy.draw()

    # Smooth camera follow
    follow_speed = 0.08
    camera_x += (player_x - camera_x) * follow_speed
    camera_y += (player_y - camera_y) * follow_speed

    # === Smooth world offset (sag effect) ===
    target_offset_x = (camera_x - player_x) * 0
    target_offset_y = (camera_y - player_y) * 0

    world_offset_x += (target_offset_x - world_offset_x) * 0.1
    world_offset_y += (target_offset_y - world_offset_y) * 0.1

    player_draw_x = WIDTH // 2 + int(world_offset_x)
    player_draw_y = HEIGHT // 2 + int(world_offset_y)

    draw_stones()
    update_sword(player_draw_x, player_draw_y)
    draw_player(player_draw_x, player_draw_y)

    pygame.display.flip()
    handle_events()
    clock.tick(60)

pygame.quit()
