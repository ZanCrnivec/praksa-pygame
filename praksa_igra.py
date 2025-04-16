import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
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
sword_base_damage = 5  # default

world_offset_x = 0
world_offset_y = 0

stones = [(random.randint(-2000, 2000), random.randint(-2000, 2000), random.randint(10, 50)) for _ in range(80)]

player_health = 100
max_health = 100

# Stamina
max_stamina = 100
player_stamina = max_stamina
stamina_regen_rate = 20
dash_stamina_cost = 40

enemy_hit_timers = {}
invincibility_duration = 1000

player_knockback = 0
player_knockback_velocity = 0
player_knockback_direction = (0, 0)
player_knockback_deceleration = 0.9

# Sword system
player_brutality = 0
player_tactics = 0
player_survival = 0


sword_type = "TACTICS"
sword_colors = {
    "BRUTALITY": (255, 0, 0),
    "TACTICS": (160, 32, 240),
    "SURVIVAL": (0, 255, 0)
}

possible_effects = ["double_crit", "freeze", "slowness", "burn", "poison"]
sword_effects = []

def generate_new_sword():
    global sword_type, sword_base_damage, sword_effects
    sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])
    sword_base_damage = random.randint(3, 7)
    num_effects = random.randint(1, 5)
    sword_effects = random.sample(possible_effects, num_effects)


def calculate_sword_damage():
    level = 0
    scale = 1
    if sword_type == "BRUTALITY":
        level = player_brutality
        scale = 1.5
    elif sword_type == "TACTICS":
        level = player_tactics
        scale = 1.2
    elif sword_type == "SURVIVAL":
        level = player_survival
        scale = 1.1
    return sword_base_damage * (scale ** level)

def get_attribute_level():
    if sword_type == "BRUTALITY":
        return player_brutality
    elif sword_type == "TACTICS":
        return player_tactics
    elif sword_type == "SURVIVAL":
        return player_survival
    return 0




def get_scaled_stats():
    hp = 100 * ((1.1 ** player_brutality) * (1.1 ** player_tactics) * (1.5 ** player_survival))
    stamina = 100 * ((1.2 ** player_brutality) * (1.5 ** player_tactics) * (1.2 ** player_survival))
    return hp, stamina

class Enemy:
    def __init__(self, x, y, speed, damage, color, size, hp):
        self.status_effects = {}
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
        distance = math.sqrt(dx ** 2 + dy ** 2)
        now = pygame.time.get_ticks()

        # Freeze
        # Freeze
        if "freeze" in self.status_effects:
            e = self.status_effects["freeze"]
            if now - e["time"] < e["duration"]:
                for _ in range(3):  # ← spawn 3 particles per frame instead of 1
                    particles.append(Particle(self.x, self.y, (0, 100, 255), behavior="freeze"))
                return
            else:
                del self.status_effects["freeze"]



        # Slowness
        speed_multiplier = 0.5 if "slowness" in self.status_effects and now - self.status_effects["slowness"]["time"] < self.status_effects["slowness"]["duration"] else 1.0
        
        if "slowness" in self.status_effects and now - self.status_effects["slowness"]["time"] < self.status_effects["slowness"]["duration"]:
            for _ in range(2):  # ← more subtle than freeze
                particles.append(Particle(self.x, self.y, (128, 128, 128), behavior="slowness"))



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
            self.x += dx * self.speed * speed_multiplier
            self.y += dy * self.speed * speed_multiplier


        if "burn" in self.status_effects:
            b = self.status_effects["burn"]
            if now - b["time"] < b["duration"]:
                if now >= b["next_tick"]:
                    burn_damage = calculate_sword_damage() * 0.1
                    self.hp -= burn_damage
                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, burn_damage))
                    b["next_tick"] = now + b["tick"]
                    for _ in range(random.randint(4, 10)):  # spawn 5 particles
                        particles.append(Particle(self.x, self.y, (255, 100, 0), behavior="burn"))

            else:
                del self.status_effects["burn"]

        if "poison" in self.status_effects:
            p = self.status_effects["poison"]
            if now - p["time"] < p["duration"]:
                if now >= p["next_tick"]:
                    poison_damage = calculate_sword_damage() * 0.3
                    self.hp -= poison_damage
                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, poison_damage))
                    p["next_tick"] = now + p["tick"]
                    for _ in range(random.randint(4, 10)):
                        particles.append(Particle(self.x, self.y, (0, 255, 0), behavior="poison"))
            else:
                del self.status_effects["poison"]
            


    def take_damage(self, damage, player_x, player_y):
        self.hp -= damage
        if self.hp > 0:
            dx = self.x - player_x
            dy = self.y - player_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance != 0:
                self.knockback_direction = (dx / distance, dy / distance)
            self.knockback = 10
            self.knockback_velocity = 10

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x - camera_x + WIDTH // 2), int(self.y - camera_y + HEIGHT // 2)), self.size)

    def is_alive(self):
        return self.hp > 0

class Particle:
    def __init__(self, x, y, color, behavior="default"):
        self.x = x
        self.y = y
        self.radius = random.randint(4, 8)
        self.color = color
        self.life = 60
        self.behavior = behavior

        if behavior == "freeze" or behavior == "slowness":
            self.vx = 0
            self.vy = 0
            self.radius *= 2
        elif behavior == "burn":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-2.5, -0.5)
        elif behavior == "poison":
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-3, 3)
        else:
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-4, 4)

    def update(self):
        if self.behavior == "burn":
            self.vy -= 0.1  # gori navzgor
            self.vx += random.uniform(-0.1, 0.1)
        elif self.behavior == "poison":
            self.vx += random.uniform(-0.3, 0.3)
            self.vy += random.uniform(-0.3, 0.3)
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



class DamageNumber:
    def __init__(self, x, y, amount, critical=False):
        self.x = x
        self.y = y
        self.amount = str(int(amount))
        self.life = 60
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2.5, -1.0)
        self.alpha = 255
        self.critical = critical
        self.font = pygame.font.SysFont(None, 48 if critical else 32)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
        self.alpha = max(0, int(255 * (self.life / 60)))

    def draw(self):
        if self.life > 0:
            color = (255, 0, 0) if self.critical else (255, 255, 0)
            text_surf = self.font.render(self.amount, True, color)
            text_surf.set_alpha(self.alpha)
            screen.blit(text_surf, (self.x - camera_x + WIDTH // 2, self.y - camera_y + HEIGHT // 2))

    def is_alive(self):
        return self.life > 0


enemy_spawn_time = 3000
last_spawn_time = 0
enemies = []
particles = []
damage_numbers = []

def spawn_enemy():
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    speed = random.uniform(0.5, 3)
    damage = random.randint(10, 20)
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    size = random.randint(30, 50)
    hp = random.randint(5, 25)
    enemies.append(Enemy(x, y, speed, damage, color, size, hp))

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
    sword_surface.fill(sword_colors[sword_type])
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
                crit = is_critical_hit()
                damage = calculate_sword_damage() * (2 if crit else 1)
                enemy.take_damage(damage, player_x, player_y)
                # Double Crit handled in crit chance function (to be modified later)

                # Apply status effects
                

                if "freeze" in sword_effects:
                    duration = 1000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["freeze"] = {"time": pygame.time.get_ticks(), "duration": duration}

                if "slowness" in sword_effects:
                    duration = 2000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["slowness"] = {"time": pygame.time.get_ticks(), "duration": duration}

                if "burn" in sword_effects:
                    duration = 3000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["burn"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": duration,
                        "tick": 300,
                        "next_tick": pygame.time.get_ticks() + 300,
                    }

                if "poison" in sword_effects:
                    duration = 6000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["poison"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": duration,
                        "tick": 1000,
                        "next_tick": pygame.time.get_ticks() + 2000,
                    }

                damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage, critical=crit))
                sword_hit_enemies.add(enemy.id)

def draw_stones():
    for stone in stones:
        draw_x = stone[0] - camera_x + WIDTH // 2 + int(world_offset_x)
        draw_y = stone[1] - camera_y + HEIGHT // 2 + int(world_offset_y)
        pygame.draw.circle(screen, (128, 128, 128), (draw_x, draw_y), stone[2])

def draw_player(x, y):
    pygame.draw.circle(screen, (255, 255, 255), (x, y), 35)

def draw_health_bar():
    bar_width = 250
    x, y = 200, 950
    ratio = player_health / max_health
    color = (int(255 * (1 - ratio)), int(255 * ratio), 0)
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, 23))
    pygame.draw.rect(screen, color, (x, y, bar_width * ratio, 23))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, 23), 2)
    font = pygame.font.SysFont(None, 24)
    hp_text = font.render(f"{int(player_health)}/{int(max_health)}", True, (255, 255, 255))
    screen.blit(hp_text, (x + bar_width + 10, y))


def draw_stamina_bar():
    bar_width = 250
    x, y = 200, 990
    ratio = player_stamina / max_stamina
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, 23))
    pygame.draw.rect(screen, (0, 200, 255), (x, y, bar_width * ratio, 23))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, 23), 2)
    font = pygame.font.SysFont(None, 24)
    stamina_text = font.render(f"{int(player_stamina)}/{int(max_stamina)}", True, (255, 255, 255))
    screen.blit(stamina_text, (x + bar_width + 10, y))


def draw_stats():
    font = pygame.font.SysFont(None, 36)
    crit_percent = round(get_crit_chance() * 100, 2)
    if "double_crit" in sword_effects:
        crit_percent *= 2


    lines = [
        ("Sword Type: " + sword_type, sword_colors[sword_type]),
        ("Base Damage: " + str(sword_base_damage), (255, 255, 255)),
        ("Total Damage: " + str(round(calculate_sword_damage(), 2)), (255, 255, 255)),
        ("Crit Chance: " + str(crit_percent) + "%", (255, 100, 100)),
        ("BRUTALITY (1): " + str(player_brutality), sword_colors["BRUTALITY"]),
        ("TACTICS (2): " + str(player_tactics), sword_colors["TACTICS"]),
        ("SURVIVAL (3): " + str(player_survival), sword_colors["SURVIVAL"]),
    ]
    for i, (text, color) in enumerate(lines):
        rendered = font.render(text, True, color)
        screen.blit(rendered, (WIDTH - 350, 30 + i * 40))
    
    effect_font = pygame.font.SysFont(None, 30)
    effect_text = effect_font.render("Effects:", True, (255, 255, 255))
    screen.blit(effect_text, (WIDTH - 350, 350))

    for i, effect in enumerate(sword_effects):
        effect_name = effect.replace("_", " ").capitalize()
        color = {
            "double_crit": (255, 255, 0),
            "freeze": (0, 100, 255),
            "slowness": (128, 128, 128),
            "burn": (255, 100, 0),
            "poison": (0, 255, 0),
        }.get(effect, (255, 255, 255))
        line = effect_font.render("- " + effect_name, True, color)
        screen.blit(line, (WIDTH - 330, 380 + i * 28))



def handle_events():
    global sword_thrust, thrust_velocity, thrust_distance, running, is_dashing, last_dash_time, dash_direction
    global player_brutality, player_tactics, player_survival
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not sword_thrust:
            sword_thrust = True
            thrust_velocity = 10
            thrust_distance = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if any([pygame.key.get_pressed()[pygame.K_w], pygame.key.get_pressed()[pygame.K_s],
                        pygame.key.get_pressed()[pygame.K_a], pygame.key.get_pressed()[pygame.K_d]]):
                    current_time = pygame.time.get_ticks()
                    if current_time - last_dash_time >= dash_cooldown and player_stamina >= dash_stamina_cost:
                        is_dashing = True
                        last_dash_time = current_time
            if event.key == pygame.K_g:
                generate_new_sword()
            if event.key == pygame.K_1:
                player_brutality += 1
            if event.key == pygame.K_2:
                player_tactics += 1
            if event.key == pygame.K_3:
                player_survival += 1


def dash():
    global player_x, player_y, is_dashing, dash_direction, player_stamina
    if is_dashing and player_stamina >= dash_stamina_cost:
        player_x += dash_direction[0] * dash_speed * 7
        player_y += dash_direction[1] * dash_speed * 7
        player_stamina -= dash_stamina_cost
        is_dashing = False

def is_critical_hit():
    base_chance = 0.01
    if sword_type == "BRUTALITY":
        crit_chance = base_chance * (1.5 ** player_brutality)
    elif sword_type == "TACTICS":
        crit_chance = base_chance * (1.6 ** player_tactics)
    elif sword_type == "SURVIVAL":
        crit_chance = base_chance * (1.2 ** player_survival)
    else:
        crit_chance = base_chance
    return random.random() < get_crit_chance()

def get_crit_chance():
    base_chance = 0.01
    multiplier = 1.0

    if sword_type == "BRUTALITY":
        multiplier = 1.2 ** player_brutality
    elif sword_type == "TACTICS":
        multiplier = 1.3 ** player_tactics
    elif sword_type == "SURVIVAL":
        multiplier = 1.1 ** player_survival

    if "double_crit" in sword_effects:
        multiplier *= 2

    return base_chance * multiplier




# Main loop
running = True
max_health, max_stamina = get_scaled_stats()
player_health = max_health
player_stamina = max_stamina

while running:
    screen.fill((26, 36, 33))
    keys = pygame.key.get_pressed()
    handle_movement(keys)

    max_health, max_stamina = get_scaled_stats()

    if player_stamina < max_stamina:
        player_stamina += stamina_regen_rate * (clock.get_time() / 1000)
        if player_stamina > max_stamina:
            player_stamina = max_stamina

    if player_knockback > 0:
        player_x += player_knockback_direction[0] * player_knockback_velocity
        player_y += player_knockback_direction[1] * player_knockback_velocity
        player_knockback_velocity *= player_knockback_deceleration
        if player_knockback_velocity < 1:
            player_knockback = 0

    direction_x = keys[pygame.K_d] - keys[pygame.K_a]
    direction_y = keys[pygame.K_s] - keys[pygame.K_w]
    if direction_x or direction_y:
        length = math.sqrt(direction_x ** 2 + direction_y ** 2)
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
                dx, dy = player_x - enemy.x, player_y - enemy.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist != 0:
                    player_knockback_direction = (dx / dist, dy / dist)
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

    player_draw_x = WIDTH // 2
    player_draw_y = HEIGHT // 2

    draw_stones()

    for p in particles:
        p.update()
        p.draw()
    particles = [p for p in particles if p.is_alive()]

    for dmg in damage_numbers:
        dmg.update()
        dmg.draw()
    damage_numbers = [d for d in damage_numbers if d.is_alive()]

    update_sword(player_draw_x, player_draw_y)
    draw_player(player_draw_x, player_draw_y)
    draw_health_bar()
    draw_stamina_bar()
    draw_stats()

    pygame.display.flip()
    handle_events()
    clock.tick(60)

pygame.quit()
