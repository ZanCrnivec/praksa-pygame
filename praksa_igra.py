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
dash_speed = 50
dash_cooldown = 500
last_dash_time = 0
is_dashing = False
dash_direction = (0, 0)

camera_x, camera_y = player_x, player_y

sword_thrust = False
thrust_velocity = 0
thrust_distance = 0
sword_hit_enemies = set()

world_offset_x = 0
world_offset_y = 0

stones = [(random.randint(-2000, 2000), random.randint(-2000, 2000), random.randint(10, 50)) for _ in range(80)]

sword_damage = 1

player_health = 100
max_health = 100

enemy_hit_timers = {}
invincibility_duration = 1000  # ms

player_knockback = 0
player_knockback_velocity = 0
player_knockback_direction = (0, 0)
player_knockback_deceleration = 0.9

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
        self.knockback_velocity = 0
        self.knockback_direction = (0, 0)
        self.knockback_deceleration = 0.9
        self.id = id(self)

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance != 0:
            dx /= distance
            dy /= distance

        if self.knockback > 0:
            self.x += self.knockback_direction[0] * self.knockback_velocity
            self.y += self.knockback_direction[1] * self.knockback_velocity
            self.knockback_velocity *= self.knockback_deceleration
            if self.knockback_velocity < 1:
                self.knockback = 0
        else:
            self.x += dx * self.speed
            self.y += dy * self.speed

    def take_damage(self, damage, player_x, player_y):
        self.hp -= damage
        if self.hp > 0:
            knockback_dx = self.x - player_x
            knockback_dy = self.y - player_y
            knockback_distance = math.sqrt(knockback_dx**2 + knockback_dy**2)
            if knockback_distance != 0:
                self.knockback_direction = (knockback_dx / knockback_distance, knockback_dy / knockback_distance)
            self.knockback = 10
            self.knockback_velocity = 10

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x - camera_x + WIDTH // 2), int(self.y - camera_y + HEIGHT // 2)), self.size)

    def is_alive(self):
        return self.hp > 0


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 7)
        self.color = color
        self.life = 60
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.radius > 0:
            self.radius -= 0.1

    def draw(self):
        if self.life > 0 and self.radius > 0:
            alpha = max(0, int(255 * (self.life / 60)))
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha), (self.radius, self.radius), int(self.radius))
            screen.blit(surface, (self.x - self.radius - camera_x + WIDTH // 2,
                                  self.y - self.radius - camera_y + HEIGHT // 2))

    def is_alive(self):
        return self.life > 0 and self.radius > 0


enemy_spawn_time = 3000
last_spawn_time = 0
enemies = []
particles = []

def spawn_enemy():
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    speed = random.uniform(0.5, 3)
    damage = random.randint(10, 20)
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    size = random.randint(30, 50)
    hp = 3
    enemy = Enemy(x, y, speed, damage, color, size, hp)
    enemies.append(enemy)

def handle_movement(keys):
    global player_x, player_y
    if player_knockback == 0:
        if keys[pygame.K_w]: player_y -= player_speed
        if keys[pygame.K_s]: player_y += player_speed
        if keys[pygame.K_a]: player_x -= player_speed
        if keys[pygame.K_d]: player_x += player_speed

def update_sword(player_draw_x, player_draw_y):
    global sword_thrust, thrust_velocity, thrust_distance, sword_hit_enemies

    if sword_thrust:
        thrust_distance += thrust_velocity
        thrust_velocity -= 1.5
        if thrust_distance <= 0:
            sword_thrust = False
            thrust_velocity = 0
            thrust_distance = 0
            sword_hit_enemies.clear()

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

    if sword_thrust and thrust_velocity > 0:
        for enemy in enemies:
            enemy_rect = pygame.Rect(int(enemy.x - camera_x + WIDTH // 2 - enemy.size),
                                     int(enemy.y - camera_y + HEIGHT // 2 - enemy.size),
                                     enemy.size * 2, enemy.size * 2)
            if sword_rect.colliderect(enemy_rect) and enemy.id not in sword_hit_enemies:
                enemy.take_damage(sword_damage, player_x, player_y)
                sword_hit_enemies.add(enemy.id)

def draw_stones():
    for stone in stones:
        draw_x = stone[0] - camera_x + WIDTH // 2 + int(world_offset_x)
        draw_y = stone[1] - camera_y + HEIGHT // 2 + int(world_offset_y)
        pygame.draw.circle(screen, (128, 128, 128), (draw_x, draw_y), stone[2])

def draw_player(player_draw_x, player_draw_y):
    pygame.draw.circle(screen, (255, 255, 255), (player_draw_x, player_draw_y), 35)

def draw_health_bar():
    bar_width = 250
    bar_height = 30
    x = 200
    y = 950
    health_ratio = player_health / max_health
    health_color = (int(255 * (1 - health_ratio)), int(255 * health_ratio), 0)
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, health_color, (x, y, bar_width * health_ratio, bar_height))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 2)

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
                if any([pygame.key.get_pressed()[pygame.K_w],
                        pygame.key.get_pressed()[pygame.K_s],
                        pygame.key.get_pressed()[pygame.K_a],
                        pygame.key.get_pressed()[pygame.K_d]]):
                    current_time = pygame.time.get_ticks()
                    if current_time - last_dash_time >= dash_cooldown:
                        is_dashing = True
                        last_dash_time = current_time

def dash():
    global player_x, player_y, is_dashing, dash_direction
    if is_dashing:
        player_x += dash_direction[0] * dash_speed * 7
        player_y += dash_direction[1] * dash_speed * 7
        is_dashing = False

running = True
while running:
    screen.fill((26, 36, 33))

    keys = pygame.key.get_pressed()
    handle_movement(keys)

    # Player knockback
    if player_knockback > 0:
        player_x += player_knockback_direction[0] * player_knockback_velocity
        player_y += player_knockback_direction[1] * player_knockback_velocity
        player_knockback_velocity *= player_knockback_deceleration
        if player_knockback_velocity < 1:
            player_knockback = 0

    direction_x, direction_y = 0, 0
    if keys[pygame.K_w]: direction_y -= 1
    if keys[pygame.K_s]: direction_y += 1
    if keys[pygame.K_a]: direction_x -= 1
    if keys[pygame.K_d]: direction_x += 1

    if direction_x != 0 or direction_y != 0:
        length = math.sqrt(direction_x**2 + direction_y**2)
        dash_direction = (direction_x / length, direction_y / length)

    dash()

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= enemy_spawn_time:
        spawn_enemy()
        last_spawn_time = current_time

    for enemy in enemies:
        enemy.move_towards_player(player_x, player_y)
        enemy.draw()

        dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
        if dist < enemy.size + 35:
            last_hit = enemy_hit_timers.get(enemy.id, 0)
            if current_time - last_hit > invincibility_duration:
                player_health -= enemy.damage
                enemy_hit_timers[enemy.id] = current_time

                # Apply knockback to player
                dx = player_x - enemy.x
                dy = player_y - enemy.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance != 0:
                    player_knockback_direction = (dx / distance, dy / distance)
                    player_knockback = 1
                    player_knockback_velocity = 15

    new_enemies = []
    for enemy in enemies:
        if enemy.is_alive():
            new_enemies.append(enemy)
        else:
            for _ in range(20):
                particles.append(Particle(enemy.x, enemy.y, enemy.color))
    enemies = new_enemies

    follow_speed = 0.08
    camera_x += (player_x - camera_x) * follow_speed
    camera_y += (player_y - camera_y) * follow_speed

    target_offset_x = (camera_x - player_x) * 0
    target_offset_y = (camera_y - player_y) * 0

    world_offset_x += (target_offset_x - world_offset_x) * 0.1
    world_offset_y += (target_offset_y - world_offset_y) * 0.1

    player_draw_x = WIDTH // 2 + int(world_offset_x)
    player_draw_y = HEIGHT // 2 + int(world_offset_y)

    draw_stones()

    for particle in particles:
        particle.update()
        particle.draw()
    particles = [p for p in particles if p.is_alive()]

    update_sword(player_draw_x, player_draw_y)
    draw_player(player_draw_x, player_draw_y)
    draw_health_bar()

    pygame.display.flip()
    handle_events()
    clock.tick(60)

pygame.quit()
