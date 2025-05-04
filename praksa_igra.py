
import pygame
import random
import math
from enum import Enum

import sqlite3

# Connect to the affixes database
affix_conn = sqlite3.connect('fixedaffixes.db')
affix_cursor = affix_conn.cursor()

score = 0
boss_spawned = False
boss_defeated = False


pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

throwing_knife_image = pygame.image.load("throw_knife.png").convert_alpha()
big_bomb_image = pygame.image.load("big_bomb.png").convert_alpha()
cannon_icon_image = pygame.image.load("cannon.png").convert_alpha()
scatter_bomb_image = pygame.image.load("scatter_bomb.png").convert_alpha()
freeze_icon_image = pygame.image.load("freeze.png").convert_alpha()
burn_icon_image = pygame.image.load("burn.png").convert_alpha()
grass_image = pygame.image.load("grass.png").convert_alpha()

rocket_spike_image = pygame.image.load("rocket_spike.png").convert_alpha()
rocket_image = pygame.image.load("rocket.png").convert_alpha()
harpooner_hat_image = pygame.image.load("harpooner_hat.png").convert_alpha()

sword_types = [
    ("Assassin Sword", "assassin_sword.png"),
    ("Balanced Blade", "balanced_sword.png"),
    ("Blood Blade", "blood_sword.png"),
    ("Broad Sword", "broad_sword.png"),
    ("Rusty Sword", "rusty_sword.png"),
    ("Spite Sword", "spite_sword.png"),
    ("Swift Blade", "swift_sword.png"),
    ("Abyssal Trident", "trident.png"),
    ("Dagger", "dagger.png"),
    ("Evil Sword", "evil_sword.png"),
    ("Deep Blade", "deep_blade.png"),
    ("Lava Sword", "lava_sword.png"),
    ("Blue Spear", "blue_spear.png"),
    ("Rapier", "rapier.png"),
    ("Katana", "katana.png"),
    ("Spike Ball", "spike_ball.png"),
    ("Boner", "boner.png"),
    ("Broken Blade", "broken_blade.png"),
    ("Cross", "cross.png"),
    ("Knight Sword", "knight_sword.png")
]




sword_images = {
    "Assassin Sword": pygame.image.load("assassin_sword.png").convert_alpha(),
    "Balanced Blade": pygame.image.load("balanced_sword.png").convert_alpha(),
    "Blood Blade": pygame.image.load("blood_sword.png").convert_alpha(),
    "Broad Sword": pygame.image.load("broad_sword.png").convert_alpha(),
    "Rusty Sword": pygame.image.load("rusty_sword.png").convert_alpha(),
    "Spite Sword": pygame.image.load("spite_sword.png").convert_alpha(),
    "Swift Blade": pygame.image.load("swift_sword.png").convert_alpha(),
    "Abyssal Trident": pygame.image.load("trident.png").convert_alpha(),
    "Dagger": pygame.image.load("dagger.png").convert_alpha(),
    "Evil Sword": pygame.image.load("evil_sword.png").convert_alpha(),
    "Deep Blade": pygame.image.load("deep_blade.png").convert_alpha(),
    "Lava Sword": pygame.image.load("lava_sword.png").convert_alpha(),
    "Blue Spear": pygame.image.load("blue_spear.png").convert_alpha(),
    "Rapier": pygame.image.load("rapier.png").convert_alpha(),
    "Katana": pygame.image.load("katana.png").convert_alpha(),
    "Spike Ball": pygame.image.load("spike_ball.png").convert_alpha(),
    "Boner": pygame.image.load("boner.png").convert_alpha(),
    "Broken Blade": pygame.image.load("broken_blade.png").convert_alpha(),
    "Cross": pygame.image.load("cross.png").convert_alpha(),
    "Knight Sword": pygame.image.load("knight_sword.png").convert_alpha(),
}

# --- Scroll System ---

scroll_images = {
    "BST": pygame.image.load("scroll_BST.png").convert_alpha(),
    "BT": pygame.image.load("scroll_BT.png").convert_alpha(),
    "BS": pygame.image.load("scroll_BS.png").convert_alpha(),
    "ST": pygame.image.load("scroll_ST.png").convert_alpha(),
}

class ScrollPickup:
    def __init__(self, x, y, scroll_type):
        self.x = x
        self.y = y
        self.scroll_type = scroll_type  # "BST", "BT", "BS", "ST"
        self.image = pygame.transform.scale(scroll_images[self.scroll_type], (140, 80))
        self.size = 40

    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        screen.blit(self.image, (draw_x - self.size, draw_y - self.size))

    def is_near_player(self):
        return math.hypot(player_x - self.x, player_y - self.y) < 80

scroll_pickups = []

def spawn_scroll():
    if len(scroll_pickups) >= 3:
        return

    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    scroll_type = random.choice(["BST", "BT", "BS", "ST"])
    scroll_pickups.append(ScrollPickup(x, y, scroll_type))

camera_shake_intensity = 0
camera_shake_decay = 0.9


# Scroll interaction state
scroll_being_opened = None
scroll_options = []
selecting_scroll_attribute = False
enemy_scaling_factor = 1.0

def open_scroll(scroll):
    global scroll_being_opened, selecting_scroll_attribute, scroll_options
    scroll_being_opened = scroll
    selecting_scroll_attribute = True

    if scroll.scroll_type == "BST":
        scroll_options = ["BRUTALITY", "TACTICS", "SURVIVAL"]
    elif scroll.scroll_type == "BT":
        scroll_options = ["BRUTALITY", "TACTICS"]
    elif scroll.scroll_type == "BS":
        scroll_options = ["BRUTALITY", "SURVIVAL"]
    elif scroll.scroll_type == "ST":
        scroll_options = ["SURVIVAL", "TACTICS"]

def draw_scroll_selection():
    if not selecting_scroll_attribute or not scroll_being_opened:
        return


    dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 180))  # Black with 180 alpha (semi-transparent)
    screen.blit(dim_surface, (0, 0))


    # Draw title
    title_font = pygame.font.SysFont(None, 72)
    title_text = title_font.render("Choose an Attribute", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title_text, title_rect)

    # Setup box layout (same as sword chest)
    box_width = 360
    box_height = 600
    spacing = 50
    total_width = len(scroll_options) * (box_width + spacing) - spacing
    start_x = (WIDTH - total_width) // 2
    y = HEIGHT // 2 - box_height // 2 + 50

    # Current player stats
    current_hp = 100 * (1.25 ** player_brutality) * (1.20 ** player_tactics) * (1.30 ** player_survival)

    if sword_1:
        current_sword1_dmg = sword_1.get_damage(player_brutality, player_tactics, player_survival)
    else:
        current_sword1_dmg = 0

    if sword_2:
        current_sword2_dmg = sword_2.get_damage(player_brutality, player_tactics, player_survival)
    else:
        current_sword2_dmg = 0

    for i, attr in enumerate(scroll_options):
        x = start_x + i * (box_width + spacing)

        # Simulate choosing this attribute
        temp_brutality = player_brutality
        temp_tactics = player_tactics
        temp_survival = player_survival

        if attr == "BRUTALITY":
            temp_brutality += 1
        elif attr == "TACTICS":
            temp_tactics += 1
        elif attr == "SURVIVAL":
            temp_survival += 1

        new_hp = 100 * (1.25 ** temp_brutality) * (1.20 ** temp_tactics) * (1.30 ** temp_survival)

        if sword_1:
            new_sword1_dmg = sword_1.get_damage(temp_brutality, temp_tactics, temp_survival)
        else:
            new_sword1_dmg = 0


        if sword_2:
            new_sword2_dmg = sword_2.get_damage(temp_brutality, temp_tactics, temp_survival)
        else:
            new_sword2_dmg = 0


        # Handle mouse hover
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, box_width, box_height)
        hover = rect.collidepoint(mouse_pos)

        # Draw the attribute box
        draw_attribute_box(
            x, y,
            attr_name=attr,
            current_hp=current_hp, new_hp=new_hp,
            current_sword1=current_sword1_dmg, new_sword1=new_sword1_dmg,
            current_sword2=current_sword2_dmg, new_sword2=new_sword2_dmg,
            hover=hover
        )


def draw_attribute_box(x, y, attr_name, current_hp, new_hp, current_sword1, new_sword1, current_sword2, new_sword2, hover=False):
    rect = pygame.Rect(x, y, 360, 600)
    
    border_color = (255, 255, 255) if hover else sword_colors.get(attr_name, (255, 255, 255))

    gradient_surface = pygame.Surface((rect.width, rect.height))
    base_color = sword_colors.get(attr_name, (80, 80, 80))
    start_color = pygame.Color(int(base_color[0] * 0.4), int(base_color[1] * 0.4), int(base_color[2] * 0.4))

    for i in range(rect.height):
        color = start_color.lerp((20, 20, 20), i / rect.height * 0.6)
        pygame.draw.line(gradient_surface, color, (0, i), (rect.width, i))

    screen.blit(gradient_surface, (x, y))
    pygame.draw.rect(screen, border_color, rect, 4)

    font = pygame.font.SysFont(None, 24)
    bold_font = pygame.font.SysFont(None, 28, bold=True)

    # Title: attribute name
    screen.blit(bold_font.render(f"{attr_name.capitalize()} +1", True, sword_colors.get(attr_name, (255, 255, 255))), (x + 15, y + 20))
    y_offset = y + 80

    # HP bonus
    hp_percent = ((new_hp / current_hp) - 1) * 100
    hp_text = f"HEALTH +{int(hp_percent)}%"
    screen.blit(font.render(hp_text, True, (0, 255, 0)), (x + 15, y_offset))
    y_offset += 30

    # Sword DMG bonus
    sword_dmg_bonus = 0
    if attr_name == "BRUTALITY":
        sword_dmg_bonus = 20
    elif attr_name == "TACTICS":
        sword_dmg_bonus = 30
    elif attr_name == "SURVIVAL":
        sword_dmg_bonus = 10

    sword_bonus_text = f"SWORD dmg +{sword_dmg_bonus}%"
    screen.blit(font.render(sword_bonus_text, True, (255, 255, 255)), (x + 15, y_offset))
    y_offset += 30

    # Ability DMG bonus
    ability_bonus_text = f"ABILITIES dmg +{50}%"
    screen.blit(font.render(ability_bonus_text, True, (255, 255, 255)), (x + 15, y_offset))
    y_offset += 50

    # Swords
    if sword_1:
        dmg_increase = new_sword1 - current_sword1
        percent_increase = int((dmg_increase / current_sword1) * 100) if current_sword1 != 0 else 0
        sword_color = sword_colors.get(sword_1.sword_type, (255, 255, 255))
        
        # Line 1: Name (colored) + dmg increase (white)
        screen.blit(font.render(f"{sword_1.sword_name} {Sword.roman_levels[sword_1.gear_level-1]}", True, sword_color), (x + 15, y_offset))
        sword_name_width = font.size(f"{sword_1.sword_name} {Sword.roman_levels[sword_1.gear_level-1]}")[0]
        screen.blit(font.render(f" +{percent_increase}% dmg", True, (255, 255, 255)), (x + 15 + sword_name_width + 5, y_offset))
        y_offset += 25

        # Line 2: (xx dmg -> yy dmg) white
        screen.blit(font.render(f"({int(current_sword1)} dmg -> {int(new_sword1)} dmg)", True, (255, 255, 255)), (x + 15, y_offset))
        y_offset += 40

    if sword_2:
        dmg_increase = new_sword2 - current_sword2
        percent_increase = int((dmg_increase / current_sword2) * 100) if current_sword2 != 0 else 0
        sword_color = sword_colors.get(sword_2.sword_type, (255, 255, 255))
        
        # Line 1
        screen.blit(font.render(f"{sword_2.sword_name} {Sword.roman_levels[sword_2.gear_level-1]}", True, sword_color), (x + 15, y_offset))
        sword_name_width = font.size(f"{sword_2.sword_name} {Sword.roman_levels[sword_2.gear_level-1]}")[0]
        screen.blit(font.render(f" +{percent_increase}% dmg", True, (255, 255, 255)), (x + 15 + sword_name_width + 5, y_offset))
        y_offset += 25

        # Line 2
        screen.blit(font.render(f"({int(current_sword2)} dmg -> {int(new_sword2)} dmg)", True, (255, 255, 255)), (x + 15, y_offset))
        y_offset += 40


    return rect




def handle_scroll_selection_click(mouse_pos):
    global selecting_scroll_attribute, scroll_being_opened
    global enemy_scaling_factor
    if not selecting_scroll_attribute:
        return

    box_width = 360
    box_height = 600
    spacing = 50
    total_width = len(scroll_options) * (box_width + spacing) - spacing
    start_x = (WIDTH - total_width) // 2
    y = HEIGHT // 2 - box_height // 2 + 50

    for i, attr in enumerate(scroll_options):
        x = start_x + i * (box_width + spacing)
        rect = pygame.Rect(x, y, box_width, box_height)
        if rect.collidepoint(mouse_pos):
            enemy_scaling_factor *= 1.08

            if attr == "BRUTALITY":
                global player_brutality
                player_brutality += 1
            elif attr == "TACTICS":
                global player_tactics
                player_tactics += 1
            elif attr == "SURVIVAL":
                global player_survival
                player_survival += 1

            global score
            score += 10

            if scroll_being_opened in scroll_pickups:
                scroll_pickups.remove(scroll_being_opened)

            selecting_scroll_attribute = False
            scroll_being_opened = None
            break

damage_flash_time = 0
damage_flash_duration = 50  # milliseconds


player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5
dash_speed = 50
dash_cooldown = 500
last_dash_time = 0
is_dashing = False
dash_direction = (0, 0)
chest_ui_weapons = []
bombs = []
selecting_ability = False
chest_being_opened = None

chest_images = {
    "common": pygame.image.load("chest_common.png").convert_alpha(),
    "rare": pygame.image.load("chest_rare.png").convert_alpha(),
    "epic": pygame.image.load("chest_epic.png").convert_alpha(),
    "legendary": pygame.image.load("chest_legendary.png").convert_alpha(),
}

chest_rarities = {
    "common": {"gear_range": (1, 2), "minor": True, "major": 0, "legendary": 0},
    "rare": {"gear_range": (2, 4), "minor": True, "major": 1, "legendary": 0.1},
    "epic": {"gear_range": (3, 6), "minor": True, "major": 2, "legendary": 0.25},
    "legendary": {"gear_range": (4, 7), "minor": True, "major": 3, "legendary": 1.0}
}

teleporter_hat_image = pygame.image.load("teleporter.png").convert_alpha()

def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_height):
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            surface.blit(font.render(line, True, color), (x, y))
            y += line_height
            line = word + " "
    if line:
        surface.blit(font.render(line, True, color), (x, y))
        y += line_height
    return y

class AbilityType(Enum):
    FREEZE = "freeze"
    BURN = "burn"         # ➡️ Dodaj to vrstico!
    BOMB_BIG = "bomb_big"
    SCATTER_BOMB = "scatter_bomb"
    THROWING_KNIFE = "throwing_knife"
    CANNON = "cannon"


knives = []
class ThrowingKnife:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 25
        self.life = 60
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.image = pygame.transform.scale(throwing_knife_image, (100, 65))  # scaled properly
        self.particles = []

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        # Create a particle behind the knife
        particle = {
            "x": self.x,
            "y": self.y,
            "radius": random.randint(2, 4),
            "life": 20
        }
        self.particles.append(particle)

        # Update particles
        for p in self.particles:
            p["life"] -= 1
            p["radius"] *= 0.9  # shrink a bit
        self.particles = [p for p in self.particles if p["life"] > 0]

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < enemy.size:
                damage = self.calculate_scaled_damage()
                enemy.take_damage(damage, player_x, player_y)
                enemy.trigger_flash((255, 255, 255))
                damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage))
                self.life = 0
                break




    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated, rect.topleft)

        # Draw particles first
        for p in self.particles:
            draw_x = int(p["x"] - camera_x + WIDTH // 2)
            draw_y = int(p["y"] - camera_y + HEIGHT // 2)
            alpha = max(0, int(255 * (p["life"] / 20)))
            particle_surf = pygame.Surface((p["radius"] * 2, p["radius"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (200, 200, 255, alpha), (p["radius"], p["radius"]), int(p["radius"]))
            screen.blit(particle_surf, (draw_x - p["radius"], draw_y - p["radius"]))

    def is_alive(self):
        return self.life > 0

# global list of knives
knives = []

class Bomb:
    def __init__(self, x, y, vx, vy, radius=1000, damage=50):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.image = pygame.transform.scale(big_bomb_image, (80, 80))
        self.life = 9999  # doesn't matter for now
        self.exploded = False
        self.explosion_radius = 350
        self.damage = damage

    def update(self):
        if not self.exploded:
            # Move
            self.x += self.vx
            self.y += self.vy

            # Slow down
            self.vx *= 0.95
            self.vy *= 0.95

            # Check if almost stopped
            if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                self.explode()

    def explode(self):
        self.exploded = True

        # Create explosion particles
        for _ in range(80):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 16)
            color = random.choice([(255, 150, 0), (255, 255, 255)])
            p = Particle(self.x, self.y, color)
            p.vx = math.cos(angle) * speed
            p.vy = math.sin(angle) * speed
            p.radius = random.randint(10, 20)
            particles.append(p)

        # Damage enemies
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.explosion_radius + enemy.size:
                enemy.take_damage(self.damage, player_x, player_y)
                enemy.trigger_flash((255, 150, 0))
                
                # ➡️ Add damage number
                damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, self.damage))

                # Knockback
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                if dx or dy:
                    length = math.hypot(dx, dy)
                    enemy.knockback_direction = (dx / length, dy / length)
                    enemy.knockback = 1
                    enemy.knockback_velocity = 12

    def draw(self):
        if not self.exploded:
            draw_x = int(self.x - camera_x + WIDTH // 2)
            draw_y = int(self.y - camera_y + HEIGHT // 2)
            
            flash_speed = 10  # how fast the flash flickers
            flash = int(pygame.time.get_ticks() / flash_speed) % 2 == 0

            if flash:
                bomb_to_draw = self.image.copy()
                bomb_to_draw.fill((80, 80, 80, 0), special_flags=pygame.BLEND_RGBA_ADD)  # brighten it slightly
                screen.blit(bomb_to_draw, (draw_x - self.image.get_width() // 2, draw_y - self.image.get_height() // 2))
            else:
                screen.blit(self.image, (draw_x - self.image.get_width() // 2, draw_y - self.image.get_height() // 2))

    def is_alive(self):
        return not self.exploded

class ScatterBomb(Bomb):
    def __init__(self, x, y, vx, vy, base_damage):
        super().__init__(x, y, vx, vy, radius=100, damage=base_damage * 0.5)  # Small initial explosion
        self.image = pygame.transform.scale(scatter_bomb_image, (60, 60))
        self.has_split = False
        self.explosion_radius = 100
        self.base_damage = base_damage


    def update(self):
        if not self.exploded:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.95
            self.vy *= 0.95

            # When it slows down enough, split
            if not self.has_split and abs(self.vx) < 1 and abs(self.vy) < 1:
                self.split()
                self.has_split = True
                self.exploded = True  # 🛑 Mark as exploded immediately
        else:
            super().update()

    def split(self):
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        for angle in angles:
            vx = math.cos(angle) * 10
            vy = math.sin(angle) * 10
            mini_bomb = Bomb(self.x, self.y, vx, vy, radius=100, damage=self.base_damage)
            mini_bomb.image = pygame.transform.scale(scatter_bomb_image, (30, 30))
            bombs.append(mini_bomb)


class Ability:
    roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]

    @property
    def is_legendary(self):
        return len(self.legendary_affixes) > 0

    def __init__(self, ability_type, ability_type_attr=None):
        self.ability_type = ability_type
        self.name = ABILITY_NAMES[self.ability_type]

        if ability_type_attr is None:
            self.ability_type_attr = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])
        else:
            self.ability_type_attr = ability_type_attr

        # Do not overwrite self.ability_type_attr here anymore!

        # Base damage depending on ability type
        self.base_damage = {
            AbilityType.FREEZE: 0,
            AbilityType.BURN: 10,
            AbilityType.BOMB_BIG: 60,
            AbilityType.SCATTER_BOMB: 30,
            AbilityType.THROWING_KNIFE: 20,
            AbilityType.CANNON: 40
        }.get(self.ability_type, 10)

        self.gear_level = random.randint(1, 7)

        # Fetch affixes from database
        self.minor_affixes = self.fetch_affixes("minor", random.randint(0, min(2, self.gear_level)))
        self.major_affixes = self.fetch_affixes("major", random.randint(0, min(2, self.gear_level // 2)))
        self.legendary_affixes = self.fetch_affixes("legendary", random.randint(0, 1)) if random.random() < 0.1 else []

        self.cooldown = self.calculate_base_cooldown()
        self.last_used = 0

    def calculate_scaled_damage(self):
        scaling_factors = {
            "BRUTALITY": 1.5,
            "TACTICS": 1.6,
            "SURVIVAL": 1.2
        }

        base = self.base_damage
        attribute = self.ability_type_attr  # Should be "BRUTALITY", "TACTICS" or "SURVIVAL"
        scaling = scaling_factors.get(attribute, 1.0)

        return base * scaling


    def calculate_base_cooldown(self):
        base_cooldowns = {
            AbilityType.FREEZE: 4000,
            AbilityType.BURN: 4000,
            AbilityType.BOMB_BIG: 5000,
            AbilityType.SCATTER_BOMB: 4500,
            AbilityType.THROWING_KNIFE: 1500,
            AbilityType.CANNON: 5500,
        }
        return base_cooldowns.get(self.ability_type, 4000)  # Default 4000ms if not found


    def calculate_scaled_damage(self):
        if self.ability_type_attr == "BRUTALITY":
            return self.base_damage * (1.2 ** player_brutality)
        elif self.ability_type_attr == "TACTICS":
            return self.base_damage * (1.3 ** player_tactics)
        elif self.ability_type_attr == "SURVIVAL":
            return self.base_damage * (1.1 ** player_survival)
        else:
            return self.base_damage


    def fetch_affixes(self, affix_type, count):
        if self.ability_type in (AbilityType.BOMB_BIG, AbilityType.SCATTER_BOMB, AbilityType.CANNON):
            group = "BOMB"
        elif self.ability_type == AbilityType.THROWING_KNIFE:
            group = "KNIFE"
        elif self.ability_type in (AbilityType.FREEZE, AbilityType.BURN):
            group = "BLAST"
        else:
            group = "BLAST"  # fallback

        affix_cursor.execute("SELECT description FROM AbilityAffixes WHERE ability_group = ? AND type = ?", (group, affix_type))
        pool = [row[0] for row in affix_cursor.fetchall()]
        return random.sample(pool, min(count, len(pool)))


    def is_ready(self, now):
        return now - self.last_used >= self.cooldown

    def activate(self, now):
        self.last_used = now
        return f"Activated {self.ability_type.value} with gear level {self.roman_levels[self.gear_level - 1]}"

    def try_activate(self):
        now = pygame.time.get_ticks()
        if not self.is_ready(now):
            return
        self.last_used = now

        if self.ability_type == AbilityType.FREEZE:
            self.activate_freeze()
        elif self.ability_type == AbilityType.BURN:
            self.activate_burn()
        elif self.ability_type == AbilityType.BOMB_BIG:
            self.spawn_bomb(radius=120, damage=self.calculate_scaled_damage() * 3)
        elif self.ability_type == AbilityType.SCATTER_BOMB:
            self.spawn_scatter_bomb()
        elif self.ability_type == AbilityType.THROWING_KNIFE:
            self.spawn_knife()
        elif self.ability_type == AbilityType.CANNON:
            self.spawn_cannon()

    def activate_freeze(self):
        cone_angle = math.radians(60)
        range_distance = 400
        now = pygame.time.get_ticks()

        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)

        for _ in range(80):
            spread = random.uniform(-cone_angle / 2, cone_angle / 2)
            blast_angle = angle + spread
            speed = random.uniform(6, 12)
            p = Particle(player_x, player_y, (100, 150, 255), behavior="freeze")
            p.vx = math.cos(blast_angle) * speed
            p.vy = math.sin(blast_angle) * speed
            particles.append(p)

        for enemy in enemies:
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            if dist < range_distance:
                enemy_angle = math.atan2(dy, dx)
                angle_diff = abs((enemy_angle - angle + math.pi) % (2 * math.pi) - math.pi)
                if angle_diff < cone_angle / 2:
                    enemy.status_effects["freeze"] = {
                        "time": now,
                        "duration": 2000 * (1.1 ** get_attribute_level())
                    }

    def activate_burn(self):
        cone_angle = math.radians(60)
        range_distance = 400
        now = pygame.time.get_ticks()

        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)

        for _ in range(80):
            spread = random.uniform(-cone_angle / 2, cone_angle / 2)
            blast_angle = angle + spread
            speed = random.uniform(6, 12)
            p = Particle(player_x, player_y, (255, 140, 0), behavior="burn")
            p.vx = math.cos(blast_angle) * speed
            p.vy = math.sin(blast_angle) * speed
            particles.append(p)

        for enemy in enemies:
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            if dist < range_distance:
                enemy_angle = math.atan2(dy, dx)
                angle_diff = abs((enemy_angle - angle + math.pi) % (2 * math.pi) - math.pi)
                if angle_diff < cone_angle / 2:
                    enemy.status_effects["burn"] = {
                        "time": now,
                        "duration": 3000 * (1.1 ** get_attribute_level()),
                        "tick_damage": 10 * get_attribute_multiplier(self.ability_type_attr),

                        "tick": 300,
                        "next_tick": now + 300
                    }

    def spawn_bomb(self, radius, damage):
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        vx = math.cos(angle) * 15
        vy = math.sin(angle) * 15
        multiplier = get_attribute_multiplier(self.ability_type_attr)
        bombs.append(Bomb(player_x, player_y, vx, vy, radius, damage * multiplier))


    def spawn_knife(self):
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        knives.append(ThrowingKnife(player_x, player_y, angle))

    def spawn_cannon(self):
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        vx = math.cos(angle) * 20
        vy = math.sin(angle) * 20
        multiplier = get_attribute_multiplier(self.ability_type_attr)
        cannonball = Bomb(player_x, player_y, vx, vy, radius=150, damage=40 * multiplier)

        cannonball.image = pygame.transform.scale(big_bomb_image, (40, 40))
        bombs.append(cannonball)

    def spawn_scatter_bomb(self):
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        vx = math.cos(angle) * 14
        vy = math.sin(angle) * 14
        scatter = ScatterBomb(player_x, player_y, vx, vy, self.calculate_scaled_damage())
        bombs.append(scatter)



def draw_score():
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (30, 30))

def get_attribute_multiplier(attr_type):
    if attr_type == "BRUTALITY":
        return 1.2 ** player_brutality
    elif attr_type == "TACTICS":
        return 1.3 ** player_tactics
    elif attr_type == "SURVIVAL":
        return 1.1 ** player_survival
    return 1.0


class ChestBase:
    def __init__(self, x, y, rarity):
        self.x = x
        self.y = y
        self.rarity = rarity
        self.image = pygame.transform.scale(chest_images[rarity], (210, 110))
        self.opened = False

    def draw(self):
        if not self.opened:
            draw_x = self.x - camera_x + WIDTH // 2
            draw_y = self.y - camera_y + HEIGHT // 2
            screen.blit(self.image, (draw_x - 32, draw_y - 32))

    def is_near_player(self):
        return math.hypot(player_x - self.x, player_y - self.y) < 80

    def open(self):
        raise NotImplementedError("Subclasses must implement this")

class SwordChest(ChestBase):
    def __init__(self, x, y, rarity):
        super().__init__(x, y, rarity)

        self.x = x
        self.y = y
        self.opened = False
        self.weapons = []
        self.weapon_spawn_times = []



    def open(self):
        global score
        score += 10

        if not self.opened:
            self.opened = True
            self.weapons = []


            for _ in range(3):
                sword = Sword()

                # Gear level based on chest rarity
                gear_min, gear_max = {
                    "common": (1, 2),
                    "rare": (2, 3),
                    "epic": (4, 5),
                    "legendary": (5, 7)
                }[self.rarity]
                sword.gear_level = random.randint(gear_min, gear_max)

                # Legendary chance based on rarity
                if self.rarity == "common":
                    sword.is_legendary = False
                elif self.rarity == "rare":
                    sword.is_legendary = random.random() < 0.10
                elif self.rarity == "epic":
                    sword.is_legendary = random.random() < 0.25
                elif self.rarity == "legendary":
                    sword.is_legendary = True

                sword.base_damage = random.randint(5 + 2 * sword.gear_level, 10 + 3 * sword.gear_level)
                sword.sword_name, sword.sword_texture = random.choice(sword_types)
                sword.sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])


                # Fetch affixes from database
                affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'minor'")
                minor_pool = [row[0] for row in affix_cursor.fetchall()]
                affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'major'")
                major_pool = [row[0] for row in affix_cursor.fetchall()]
                affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'legendary'")
                legendary_pool = [row[0] for row in affix_cursor.fetchall()]

                if sword.is_legendary:
                    sword.major_affixes = ["colorless"]
                    sword.legendary_affixes = random.sample(legendary_pool, k=min(random.randint(1, 2), len(legendary_pool)))

                else:
                    sword.minor_affixes = random.sample(minor_pool, k=min(random.randint(1, sword.gear_level), len(minor_pool)))
                    if random.random() < 0.3 and major_pool:
                        sword.major_affixes = [random.choice(major_pool)]

                self.weapons.append(sword)
                self.weapon_spawn_times.append(pygame.time.get_ticks())

    def update(self):
        now = pygame.time.get_ticks()
        for i in reversed(range(len(self.weapons))):
            if now - self.weapon_spawn_times[i] > 10000:
                self.weapons.pop(i)
                self.weapon_spawn_times.pop(i)


    # Original SwordChest draw
    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)

        if not self.opened:
            screen.blit(self.image, (draw_x - 32, draw_y - 32))
        else:
            for i, sword in enumerate(self.weapons):
                sword_box_width = 100
                sword_box_height = 150
                sword_x = draw_x + i * 120 - 120
                sword_y = draw_y - 100

                # Color based on sword type
                attr_color = sword_colors.get(sword.sword_type, (255, 255, 255))

                # Draw box
                pygame.draw.rect(screen, attr_color, (sword_x, sword_y, sword_box_width, sword_box_height), border_radius=8)

                # Draw sword name
                font = pygame.font.SysFont(None, 20)
                name_text = font.render(sword.sword_name, True, (0, 0, 0))
                name_rect = name_text.get_rect(center=(sword_x + sword_box_width//2, sword_y + 20))
                screen.blit(name_text, name_rect)

                # Draw gear level
                roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]
                level_text = font.render(roman_levels[sword.gear_level - 1], True, (0, 0, 0))
                level_rect = level_text.get_rect(center=(sword_x + sword_box_width//2, sword_y + 50))
                screen.blit(level_text, level_rect)




ABILITY_NAMES = {
    AbilityType.BOMB_BIG: "Big Bomb",
    AbilityType.SCATTER_BOMB: "Scatter Bomb",
    AbilityType.CANNON: "Cannon",
    AbilityType.THROWING_KNIFE: "Throwing Knife",
    AbilityType.FREEZE: "Frost Blast",
    AbilityType.BURN: "Burn Blast"
}


class AbilityChest(ChestBase):
    def __init__(self, x, y, rarity):
        super().__init__(x, y, rarity)

        self.x = x
        self.y = y
        self.opened = False
        self.abilities = []
        self.ability_spawn_times = []


    def open(self):
        global score
        score += 10

        if not self.opened:
            self.opened = True
            self.abilities = []

            for _ in range(3):
                ability_type = random.choice([
                    AbilityType.FREEZE, AbilityType.BURN, AbilityType.BOMB_BIG,
                    AbilityType.SCATTER_BOMB, AbilityType.THROWING_KNIFE, AbilityType.CANNON
                ])
                ability = Ability(ability_type)

                # Gear level based on chest rarity
                gear_min, gear_max = {
                    "common": (1, 2),
                    "rare": (2, 3),
                    "epic": (4, 5),
                    "legendary": (5, 7)
                }[self.rarity]
                ability.gear_level = random.randint(gear_min, gear_max)

                # Base damage
                ability.base_damage = {
                    AbilityType.FREEZE: 0,
                    AbilityType.BURN: 10,
                    AbilityType.BOMB_BIG: 60,
                    AbilityType.SCATTER_BOMB: 30,
                    AbilityType.THROWING_KNIFE: 20,
                    AbilityType.CANNON: 40,
                }.get(ability.ability_type, 10)

                # Fetch affixes from database
                affix_cursor.execute("SELECT description FROM AbilityAffixes WHERE type = 'minor'")
                minor_pool = [row[0] for row in affix_cursor.fetchall()]
                affix_cursor.execute("SELECT description FROM AbilityAffixes WHERE type = 'major'")
                major_pool = [row[0] for row in affix_cursor.fetchall()]
                affix_cursor.execute("SELECT description FROM AbilityAffixes WHERE type = 'legendary'")
                legendary_pool = [row[0] for row in affix_cursor.fetchall()]

                # Minor affixes always possible
                ability.minor_affixes = random.sample(minor_pool, k=min(random.randint(0, min(2, ability.gear_level)), len(minor_pool)))

                # Major affixes depending on chest rarity
                if self.rarity in ("rare", "epic", "legendary") and major_pool:
                    ability.major_affixes = random.sample(major_pool, k=min(random.randint(1, 2), len(major_pool)))
                else:
                    ability.major_affixes = []

                # Legendary affixes depending on chest rarity
                if self.rarity == "epic" and random.random() < 0.25 and legendary_pool:
                    ability.legendary_affixes = random.sample(legendary_pool, k=min(1, len(legendary_pool)))
                elif self.rarity == "legendary" and legendary_pool:
                    ability.legendary_affixes = random.sample(legendary_pool, k=min(1, len(legendary_pool)))
                else:
                    ability.legendary_affixes = []

                ability.cooldown = ability.calculate_base_cooldown()
                self.abilities.append(ability)
                self.ability_spawn_times.append(pygame.time.get_ticks())


    def update(self):
        now = pygame.time.get_ticks()
        for i in reversed(range(len(self.abilities))):
            if now - self.ability_spawn_times[i] > 10000:
                self.abilities.pop(i)
                self.ability_spawn_times.pop(i)


    # Original AbilityChest draw
    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)

        if not self.opened:
            screen.blit(self.image, (draw_x - 32, draw_y - 32))

        else:
            for i, ability in enumerate(self.abilities):
                ability_box_width = 100
                ability_box_height = 150
                ability_x = draw_x + i * 120 - 120
                ability_y = draw_y - 100

                # Color based on ability type
                attr_color = sword_colors.get(ability.ability_type_attr, (255, 255, 255))

                # Draw box
                pygame.draw.rect(screen, attr_color, (ability_x, ability_y, ability_box_width, ability_box_height), border_radius=8)

                # Draw ability name
                font = pygame.font.SysFont(None, 20)
                name_text = font.render(ability.name, True, (0, 0, 0))
                name_rect = name_text.get_rect(center=(ability_x + ability_box_width//2, ability_y + 20))
                screen.blit(name_text, name_rect)

                # Draw gear level
                roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]
                level_text = font.render(roman_levels[ability.gear_level - 1], True, (0, 0, 0))
                level_rect = level_text.get_rect(center=(ability_x + ability_box_width//2, ability_y + 50))
                screen.blit(level_text, level_rect)





chests = []

def spawn_chest():
    if len(chests) >= 5:
        return

    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)

    if score < 100:
        rarity = "common"
    elif score < 200:
        rarity = random.choice(["common", "rare"])
    elif score < 400:
        rarity = random.choice(["rare", "epic"])
    elif score < 700:
        rarity = random.choice(["epic", "legendary"])
    else:
        rarity = "legendary"

    chest_class = random.choice([SwordChest, AbilityChest])
    chests.append(chest_class(x, y, rarity))


speed_boost_active = False
speed_boost_timer = 0
speed_boost_duration = 5000  # in ms
speed_boost_amount = 2

camera_x, camera_y = player_x, player_y

# Apply camera shake
if camera_shake_intensity > 0.5:
    camera_x += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
    camera_y += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
    camera_shake_intensity *= camera_shake_decay
else:
    camera_shake_intensity = 0


sword_thrust = False
thrust_velocity = 0
thrust_distance = 0
sword_hit_enemies = set()

world_offset_x = 0
world_offset_y = 0

stones = [(random.randint(-2000, 2000), random.randint(-2000, 2000), random.randint(10, 50)) for _ in range(80)]

player_health = 100
max_health = 100

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

sword_colors = {
    "BRUTALITY": (255, 0, 0),
    "TACTICS": (160, 32, 240),
    "SURVIVAL": (0, 255, 0)
}

possible_effects = ["double_crit", "freeze", "slowness", "burn", "poison"]

def draw_custom_ui():
    font = pygame.font.SysFont(None, 48)
    attr_y = HEIGHT - 60
    attr_x = 30

    # Attributes
    attr_values = [
        (player_brutality, sword_colors["BRUTALITY"]),
        (player_tactics, sword_colors["TACTICS"]),
        (player_survival, sword_colors["SURVIVAL"]),
    ]

    for i, (value, color) in enumerate(attr_values):
        text = font.render(str(value), True, color)
        screen.blit(text, (attr_x + i * 50, attr_y))

    # Health Bar
    bar_x = attr_x + 150
    bar_y = attr_y 
    bar_height = 30
    bar_width = int(max_health) * 2  # scale bar width based on max health
    
    ratio = player_health / max_health
    fill_width = bar_width * ratio

    # Background + fill
    pygame.draw.rect(screen, (0, 180, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (180, 255, 80), (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, (0, 100, 0), (bar_x, bar_y, bar_width, bar_height), 4)

    # Centered text
    text = font.render(f"{int(max_health)}/{int(player_health)}", True, (0, 0, 0))
    text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    screen.blit(text, text_rect)


def get_ability_icon(ability_type):
    if ability_type == AbilityType.FREEZE:
        return pygame.image.load("freeze.png").convert_alpha()
    elif ability_type == AbilityType.BURN:
        return pygame.image.load("burn.png").convert_alpha()
    elif ability_type == AbilityType.BOMB_BIG:
        return big_bomb_image
    elif ability_type == AbilityType.SCATTER_BOMB:
        return scatter_bomb_image
    elif ability_type == AbilityType.THROWING_KNIFE:
        return throwing_knife_image
    elif ability_type == AbilityType.CANNON:
        return cannon_icon_image
    return None

def draw_equipped_slots():
    slot_size = 70
    spacing = 12
    section_gap = 40  # gap between weapon and ability slots
    start_x = 30
    start_y = HEIGHT - 140
    font = pygame.font.SysFont(None, 24)
    number_font = pygame.font.SysFont(None, 22)

    slots = [sword_1, sword_2, player_ability_1, player_ability_2]

    def get_ability_icon(ability_type):
        if ability_type == AbilityType.FREEZE:
            return freeze_icon_image
        elif ability_type == AbilityType.BURN:
            return burn_icon_image
        elif ability_type == AbilityType.BOMB_BIG:
            return big_bomb_image
        elif ability_type == AbilityType.SCATTER_BOMB:
            return scatter_bomb_image
        elif ability_type == AbilityType.THROWING_KNIFE:
            return throwing_knife_image
        elif ability_type == AbilityType.CANNON:
            return cannon_icon_image
        return None

    for i, item in enumerate(slots):
        x = start_x + i * (slot_size + spacing) + (section_gap if i >= 2 else 0)
        y = start_y

        rect = pygame.Rect(x, y, slot_size, slot_size)
        pygame.draw.rect(screen, (0, 0, 0), rect.inflate(6, 6), 4)
        # Draw number label above slot
        number_text = number_font.render(str(i + 1), True, (255, 255, 255))
        num_rect = number_text.get_rect(center=(x + slot_size // 2, y - 12))
        screen.blit(number_text, num_rect)

        # Determine attribute type
        # Determine attribute color
        base_color = (60, 60, 60)  # default gray
        is_legendary = False

        if item:
            if hasattr(item, "sword_type"):
                attr_key = item.sword_type
            elif hasattr(item, "ability_type_attr"):
                attr_key = item.ability_type_attr
            else:
                attr_key = None

            if attr_key in sword_colors:
                base_color = sword_colors[attr_key]

            is_legendary = getattr(item, "is_legendary", False)

        # Gradient background
        gradient_surface = pygame.Surface((slot_size, slot_size))

        if is_legendary:
            # If legendary, full gold background
            gradient_surface.fill((255, 215, 0))
        else:
            # Normal attribute gradient
            start_color = pygame.Color(*base_color)
            end_color = pygame.Color(
                int(base_color[0] * 0.2),
                int(base_color[1] * 0.2),
                int(base_color[2] * 0.2)
            )
            for y_pos in range(slot_size):
                blend = y_pos / slot_size
                color = start_color.lerp(end_color, blend)
                pygame.draw.line(gradient_surface, color, (0, y_pos), (slot_size, y_pos))

        screen.blit(gradient_surface, (x, y))

        # --- No more "wide border if legendary" needed ---


        # Thin white outline for selection
        if (i == 0 and current_sword == sword_1) or (i == 1 and current_sword == sword_2):
            pygame.draw.rect(screen, (255, 255, 255), rect, 4)
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        
        # Inner color (thin square)
        if item:
            if hasattr(item, "sword_type"):
                attr_key = item.sword_type
            elif hasattr(item, "ability_type_attr"):
                attr_key = item.ability_type_attr
            else:
                attr_key = ""
            inner_color = sword_colors.get(attr_key, (0, 0, 0))
            inner_rect = rect.inflate(-80, -80)
            pygame.draw.rect(screen, inner_color, inner_rect)


        # Weapon icons (rotated)
        if i < 2 and item:
            icon = sword_images.get(item.sword_name)
            if icon:
                icon_scaled = pygame.transform.scale(icon, (75, 45))  # elongate
                icon_rotated = pygame.transform.rotate(icon_scaled, 45)
                icon_rect = icon_rotated.get_rect(center=rect.center)
                screen.blit(icon_rotated, icon_rect)

        # Highlight selected sword
        if (i == 0 and current_sword == sword_1) or (i == 1 and current_sword == sword_2):
            pygame.draw.rect(screen, (255, 255, 255), rect, 5)

        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.CANNON:
            icon = pygame.transform.scale(cannon_icon_image, (80, 80))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)

        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.BOMB_BIG:
            icon = pygame.transform.scale(big_bomb_image, (60, 60))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)

        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.SCATTER_BOMB:
            icon = pygame.transform.scale(scatter_bomb_image, (80, 80))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.FREEZE:
            icon = pygame.transform.scale(freeze_icon_image, (60, 60))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.BURN:
            icon = pygame.transform.scale(burn_icon_image, (60, 60))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        elif i >= 2 and item and getattr(item, "ability_type", None) == AbilityType.THROWING_KNIFE:
            icon = pygame.transform.scale(throwing_knife_image, (80, 50))
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)


        # Ability cooldown overlay
        if i >= 2 and item:
            now = pygame.time.get_ticks()
            elapsed = now - item.last_used
            cooldown = item.cooldown
            if elapsed < cooldown:
                percent = 1 - (elapsed / cooldown)
                height = int(slot_size * percent)
                overlay = pygame.Surface((slot_size, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (x, y + slot_size - height))

                remaining_sec = int((cooldown - elapsed) / 1000) + 1
                cooldown_text = font.render(str(remaining_sec), True, (255, 255, 255))
                text_rect = cooldown_text.get_rect(center=(x + slot_size // 2, y + slot_size // 2))
                screen.blit(cooldown_text, text_rect)

            else:
                # Flash for 0.2 seconds after ability is ready
                flash_duration = 200  # milliseconds
                time_since_ready = now - (item.last_used + cooldown)
                if time_since_ready < flash_duration:
                    flash_surface = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
                    alpha = int(255 * (1 - time_since_ready / flash_duration))
                    flash_surface.fill((255, 255, 255, alpha))
                    screen.blit(flash_surface, (x, y))

def generate_new_sword(sword):
    sword.generate_random()

def calculate_sword_damage():
    return current_sword.get_damage(player_brutality, player_tactics, player_survival)

def get_attribute_level():
    return current_sword.get_attribute_level(player_brutality, player_tactics, player_survival)

def get_scaled_stats():
    hp = 100 * ((1.25 ** player_brutality) * (1.20 ** player_tactics) * (1.30 ** player_survival))
    return hp

class Sword:
    roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]

    def __init__(self, sword_type="TACTICS", base_damage=5, effects=None):
        self.gear_level = 1
        self.sword_type = sword_type
        self.base_damage = base_damage
        self.effects = effects or []

        self.minor_affixes = []
        self.major_affixes = []
        self.legendary_affixes = []
        self.is_legendary = False

    def generate_random(self):
        self.minor_affixes = []
        self.major_affixes = []
        self.legendary_affixes = []

        self.gear_level = random.randint(1, 7)
        self.is_legendary = random.random() < 0.05  # 5% chance
        self.base_damage = random.randint(5 + 2 * self.gear_level, 10 + 3 * self.gear_level)

        self.sword_name, self.sword_texture = random.choice(sword_types)  # ✅ random sword name and texture
        self.sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])  # ✅ random attribute

        # Fetch from database
        affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'minor'")
        minor_pool = [row[0] for row in affix_cursor.fetchall()]
        affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'major'")
        major_pool = [row[0] for row in affix_cursor.fetchall()]
        affix_cursor.execute("SELECT description FROM SwordAffixes WHERE type = 'legendary'")
        legendary_pool = [row[0] for row in affix_cursor.fetchall()]

        
        if self.is_legendary:
            self.major_affixes = ["colorless"]
            # Add 1–2 legendary affixes randomly
            self.legendary_affixes = random.sample(legendary_pool, k=min(random.randint(1, 3), len(legendary_pool)))

        else:
            self.minor_affixes = random.sample(minor_pool, k=min(random.randint(1, self.gear_level), len(minor_pool)))
            if random.random() < 0.3 and major_pool:
                self.major_affixes = [random.choice(major_pool)]

    def get_damage(self, brutality, tactics, survival, target=None, is_crit=False):
        # Base multiplier from attribute
        if self.sword_type == "BRUTALITY":
            multiplier = 1.2 ** brutality
        elif self.sword_type == "TACTICS":
            multiplier = 1.3 ** tactics
        elif self.sword_type == "SURVIVAL":
            multiplier = 1.1 ** survival
        else:
            multiplier = 1.0

        damage = self.base_damage * multiplier

        # --- Minor affixes ---
        if "+20% damage" in self.minor_affixes:
            damage *= 1.2

        if "+50% damage when you are at max HP" in self.minor_affixes and player_health == max_health:
            damage *= 1.5

        if is_crit:
            if "Critical hits +20% damage" in self.minor_affixes:
                damage *= 1.2
            if "Critical hits +30% damage" in self.minor_affixes:
                damage *= 1.3

        if target:
            if "+40% damage on burning target" in self.minor_affixes and "burn" in target.status_effects:
                damage *= 1.4
            if "+40% damage on poisoned target" in self.minor_affixes and "poison" in target.status_effects:
                damage *= 1.4
            if "+40% damage on frozen target" in self.minor_affixes and "freeze" in target.status_effects:
                damage *= 1.4
            if "+40% damage on slowed target" in self.minor_affixes and "slowness" in target.status_effects:
                damage *= 1.4

        # --- Major affixes ---
        if "+15% damage" in self.major_affixes:
            damage *= 1.15
        if "+40% damage" in self.major_affixes:
            damage *= 1.4
        if "+100% damage inflicted on enemies, +100% damage taken!" in self.major_affixes:
            damage *= 2
        if "+300% damage inflicted on enemies, +300% damage taken!" in self.major_affixes:
            damage *= 4
        if "colorless" in self.major_affixes:
            # Set sword type to player's highest attribute
            max_attr = max(player_brutality, player_tactics, player_survival)
            if player_brutality == max_attr:
                self.sword_type = "BRUTALITY"
            elif player_tactics == max_attr:
                self.sword_type = "TACTICS"
            elif player_survival == max_attr:
                self.sword_type = "SURVIVAL"

        # --- Legendary affixes ---
        if "+300% damage inflicted on enemies!" in self.legendary_affixes:
            damage *= 4

        return damage

    def get_attribute_level(self, brutality, tactics, survival):
        if self.sword_type == "BRUTALITY":
            return brutality
        elif self.sword_type == "TACTICS":
            return tactics
        elif self.sword_type == "SURVIVAL":
            return survival
        return 0



player_ability_1 = Ability(AbilityType.FREEZE)  # 🔵 freeze on slot 1
player_ability_2 = Ability(AbilityType.BURN)    # 🟠 burn on slot 2

player_ability_1 = None
player_ability_2 = None

sword_1 = None
sword_2 = None
current_sword = None

# Create a starting rusty sword
rusty_sword = Sword()
rusty_sword.sword_name = "Rusty Sword"
rusty_sword.sword_type = "BRUTALITY"
rusty_sword.base_damage = 9
rusty_sword.gear_level = 1
rusty_sword.minor_affixes = []
rusty_sword.major_affixes = []
rusty_sword.legendary_affixes = []
rusty_sword.is_legendary = False
rusty_sword.sword_texture = "rusty_sword.png"  # <-- ADD THIS


# Assign starting swords
sword_1 = rusty_sword
sword_2 = None
current_sword = sword_1


def check_sword_hits_harpoon(player_x, player_y, sword_range=50):
    for enemy in enemies:
        if enemy.type == "harpooner" and enemy.harpoon_state in ("shooting", "pulling"):
            # Get harpoon line points
            start_x, start_y = enemy.x, enemy.y
            end_x, end_y = enemy.harpoon_pos[0], enemy.harpoon_pos[1]

            # Calculate distance from player to line segment
            line_mag = math.hypot(end_x - start_x, end_y - start_y)
            if line_mag == 0:
                continue  # No line, skip

            # Closest point on line
            u = ((player_x - start_x) * (end_x - start_x) + (player_y - start_y) * (end_y - start_y)) / (line_mag ** 2)
            u = max(min(u, 1), 0)
            closest_x = start_x + u * (end_x - start_x)
            closest_y = start_y + u * (end_y - start_y)

            # Distance from player to closest point on harpoon line
            distance = math.hypot(player_x - closest_x, player_y - closest_y)

            if distance < sword_range:
                # Sword hits harpoon line!
                enemy.harpoon_state = "idle"
                break  # One hit is enough


# Auto-equip throwing knife in ability slot 1

class Enemy:
    def __init__(self, enemy_type="normal"):
        self.status_effects = {}
        self.type = enemy_type  # "normal" or "rocketeer"
        self.x = random.randint(-2000, 2000)
        self.y = random.randint(-2000, 2000)
        self.id = id(self)

        # General common properties
        self.knockback = 0
        self.knockback_velocity = 0
        self.knockback_direction = (0, 0)
        self.knockback_deceleration = 0.9
        self.flash_color = None
        self.flash_time = 0
        self.flash_duration = 100  # milliseconds

        # Rocketeer-related properties (initialize for all)
        self.fire_cooldown = 2000
        self.last_shot_time = pygame.time.get_ticks()
        self.charging = 0

        # Then assign specific enemy stats
        if self.type == "rocketeer":
            self.speed = random.uniform(1.2, 2.0)
            self.size = random.randint(45, 60)
            self.base_color = [random.randint(100, 255) for _ in range(3)]
            self.color = self.base_color.copy()
            self.damage = 15
            self.hp = int(50 * enemy_scaling_factor)
        elif self.type == "harpooner":
            self.speed = random.uniform(1.5, 2.5)
            self.size = random.randint(40, 55)
            self.base_color = [random.randint(150, 255) for _ in range(3)]
            self.color = self.base_color.copy()
            self.damage = 30
            self.hp = int(45 * enemy_scaling_factor)
            
            # Harpoon-specific
            self.harpoon_state = "idle"
            self.harpoon_pos = [self.x, self.y]
            self.harpoon_velocity = [0, 0]
            self.latched = False
            self.just_hit_player = False  # Used to deal damage outside
        elif self.type == "teleporter":
            self.speed = random.uniform(2.5, 4.0)
            self.size = random.randint(35, 50)
            self.base_color = [random.randint(100, 255) for _ in range(3)]
            self.color = self.base_color.copy()
            self.damage = 20
            self.hp = int(40 * enemy_scaling_factor)
            self.next_teleport_time = pygame.time.get_ticks() + random.randint(2000, 5000)
        elif self.type == "conjivictus":
            self.speed = random.uniform(4.5, 6.5)  # Fast but not teleport
            self.size = random.randint(80, 100)    # Around 2× normal enemies
            self.base_color = [random.randint(100, 255) for _ in range(3)]
            self.color = self.base_color.copy()
            self.damage = 30
            self.hp = 500
            self.next_move_time = pygame.time.get_ticks()
            self.state = "moving"  # states: moving, preparing, attacking
            self.attack_type = None
            self.attack_timer = 0
            self.attack_rotation = 0
            self.zone_spawn_times = []
            self.zones = []
        else:
            self.speed = random.uniform(2.0, 4.0)
            self.size = random.randint(25, 50)
            self.color = (255, 0, 0)
            self.damage = 20
            self.hp = int(40 * enemy_scaling_factor)


    def trigger_flash(self, color):
        self.flash_color = color
        self.flash_time = pygame.time.get_ticks()

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        now = pygame.time.get_ticks()

        # Freeze handling
        if "freeze" in self.status_effects:
            e = self.status_effects["freeze"]
            if now - e["time"] < e["duration"]:
                if "last_particle" not in e or now - e["last_particle"] > 200:
                    offset_x = random.uniform(-self.size, self.size)
                    offset_y = random.uniform(-self.size, self.size)
                    particles.append(Particle(self.x + offset_x, self.y + offset_y, (0, 100, 255), behavior="freeze"))
                    e["last_particle"] = now
                return
            else:
                del self.status_effects["freeze"]

        # Slowness effect
        speed_multiplier = 0.5 if "slowness" in self.status_effects and now - self.status_effects["slowness"]["time"] < self.status_effects["slowness"]["duration"] else 1.0

        if distance != 0:
            dx /= distance
            dy /= distance

        if self.knockback > 0:
            # Knockback handling
            self.x += self.knockback_direction[0] * self.knockback_velocity
            self.y += self.knockback_direction[1] * self.knockback_velocity
            self.knockback_velocity *= self.knockback_deceleration
            if self.knockback_velocity < 1:
                self.knockback = 0
        else:
            if self.type == "rocketeer":
                if distance > 600:
                    # Approach player if too far
                    self.x += dx * self.speed * speed_multiplier
                    self.y += dy * self.speed * speed_multiplier
                else:
                    # Move away if too close
                    self.x -= dx * self.speed * speed_multiplier
                    self.y -= dy * self.speed * speed_multiplier

                # Fire rockets
                if now - self.last_shot_time >= self.fire_cooldown:
                    dx = player_x - self.x
                    dy = player_y - self.y
                    angle = math.atan2(dy, dx)
                    rockets.append(Rocket(self.x, self.y, angle))

                    self.last_shot_time = now

            elif self.type == "harpooner":
                if self.harpoon_state == "idle":
                    if distance > 500:
                        self.x += dx * self.speed * speed_multiplier
                        self.y += dy * self.speed * speed_multiplier
                    else:
                        # Start shooting harpoon
                        self.harpoon_state = "shooting"
                        dir_to_player = math.atan2(dy, dx)
                        harpoon_speed = 16  # Faster now
                        self.harpoon_velocity = [math.cos(dir_to_player) * harpoon_speed, math.sin(dir_to_player) * harpoon_speed]
                        self.harpoon_pos = [self.x, self.y]

                elif self.harpoon_state in ("shooting", "returning"):
                    # Slightly home towards the player while shooting/returning
                    dx_harp = player_x - self.harpoon_pos[0]
                    dy_harp = player_y - self.harpoon_pos[1]
                    angle_to_player = math.atan2(dy_harp, dx_harp)

                    # Adjust velocity slightly toward player
                    current_angle = math.atan2(self.harpoon_velocity[1], self.harpoon_velocity[0])
                    diff = (angle_to_player - current_angle + math.pi) % (2 * math.pi) - math.pi
                    current_angle += diff * 0.05  # gentle homing

                    harpoon_speed = 16  # keep it fast
                    self.harpoon_velocity = [math.cos(current_angle) * harpoon_speed, math.sin(current_angle) * harpoon_speed]

                    self.harpoon_pos[0] += self.harpoon_velocity[0]
                    self.harpoon_pos[1] += self.harpoon_velocity[1]

                    # Check collision with player anytime during shooting/returning
                    # Vector from harpooner to harpoon tip
                    line_dx = self.harpoon_pos[0] - self.x
                    line_dy = self.harpoon_pos[1] - self.y

                    # Vector from harpooner to player
                    player_dx = player_x - self.x
                    player_dy = player_y - self.y

                    # Project player onto the harpoon line
                    line_length = math.hypot(line_dx, line_dy)
                    if line_length == 0:
                        line_length = 0.001  # prevent division by zero

                    # Normalize harpoon line
                    line_dir_x = line_dx / line_length
                    line_dir_y = line_dy / line_length

                    # Projection scalar
                    proj_length = player_dx * line_dir_x + player_dy * line_dir_y

                    # Clamp projection to [0, line_length]
                    proj_length = max(0, min(line_length, proj_length))

                    # Closest point on the line
                    closest_x = self.x + line_dir_x * proj_length
                    closest_y = self.y + line_dir_y * proj_length

                    # Distance from player to closest point
                    dist_to_line = math.hypot(player_x - closest_x, player_y - closest_y)

                    # If player is close enough to the line (say 20-30 pixels), latch
                    if dist_to_line < 30:
                        self.latched = True
                        self.harpoon_state = "pulling"

                        # Immediately start pulling faster
                        pull_dx = player_x - self.x
                        pull_dy = player_y - self.y
                        pull_distance = math.hypot(pull_dx, pull_dy)
                        if pull_distance != 0:
                            pull_dx /= pull_distance
                            pull_dy /= pull_distance
                            self.x += pull_dx * self.speed * 4
                            self.y += pull_dy * self.speed * 4



                    if self.harpoon_state == "shooting" and math.hypot(self.harpoon_pos[0] - self.x, self.harpoon_pos[1] - self.y) > 800:
                        # If reached max distance during shooting, return
                        return_dir = math.atan2(self.y - self.harpoon_pos[1], self.x - self.harpoon_pos[0])
                        self.harpoon_velocity = [math.cos(return_dir) * 10, math.sin(return_dir) * 10]
                        self.harpoon_state = "returning"

                    if self.harpoon_state == "returning" and math.hypot(self.harpoon_pos[0] - self.x, self.harpoon_pos[1] - self.y) < 10:
                        # If returned
                        self.harpoon_state = "idle"

                elif self.harpoon_state == "pulling":
                    self.x += (player_x - self.x) * 0.2
                    self.y += (player_y - self.y) * 0.2

                    if distance < 20:
                        self.just_hit_player = True
                        self.harpoon_state = "running"
                        self.latched = False

                elif self.harpoon_state == "running":
                    self.x -= dx * self.speed * 2 * speed_multiplier
                    self.y -= dy * self.speed * 2 * speed_multiplier


            elif self.type == "teleporter":
                # Move towards player
                self.x += dx * self.speed * speed_multiplier
                self.y += dy * self.speed * speed_multiplier

                # Auto teleport check
                if now >= self.next_teleport_time:
                    teleport_distance = random.randint(200, 300)

                    # Sword direction from player to mouse
                    mx, my = pygame.mouse.get_pos()
                    sword_angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
                    teleport_angle = sword_angle + math.pi  # Opposite direction

                    old_x, old_y = self.x, self.y
                    self.x = player_x + math.cos(teleport_angle) * teleport_distance
                    self.y = player_y + math.sin(teleport_angle) * teleport_distance

                    # Purple teleport particles
                    for _ in range(15):
                        particles.append(Particle(
                            old_x + random.randint(-10, 10),
                            old_y + random.randint(-10, 10),
                            (150, 0, 255),
                            behavior="teleport"
                        ))

                    for _ in range(15):
                        particles.append(Particle(
                            self.x + random.randint(-10, 10),
                            self.y + random.randint(-10, 10),
                            (150, 0, 255),
                            behavior="teleport"
                        ))
                    # Set next teleport time (2–5 sec)
                    self.next_teleport_time = now + random.randint(2000, 5000)
            elif self.type == "conjivictus":

                if self.state == "moving":
                    dx = player_x - self.x
                    dy = player_y - self.y
                    distance = math.hypot(dx, dy)

                    if distance != 0:
                        dx /= distance
                        dy /= distance

                    self.x += dx * (self.speed * 2)  # Fast movement toward player
                    self.y += dy * (self.speed * 2)

                    # Check collision with player during moving
                    if math.hypot(player_x - self.x, player_y - self.y) < self.size:
                        global player_health
                        player_health -= 30
                        camera_shake_intensity = 15  # set initial shake strength
                        damage_flash_time = pygame.time.get_ticks()


                        # Set player knockback properly
                        player_knockback = 1
                        player_knockback_direction = (-dx, -dy)  # move away from enemy
                        player_knockback_velocity = 20  # Adjust velocity if needed

                        # Set boss knockback
                        self.knockback = 1
                        self.knockback_direction = (dx, dy)
                        self.knockback_velocity = 30  # Boss gets a strong push back


                    if now > self.next_move_time:
                        self.state = "preparing"
                        self.next_move_time = now + 1000  # Prepare 1 second before attack

                elif self.state == "preparing":
                    if now > self.next_move_time:
                        # Move boss slightly away before attacking
                        dx = self.x - player_x
                        dy = self.y - player_y
                        distance = math.hypot(dx, dy)
                        if distance != 0:
                            dx /= distance
                            dy /= distance

                        self.x += dx * 100  # Push boss 100px away from player
                        self.y += dy * 100

                        self.state = "attacking"
                        self.attack_type = random.choice(["spiral", "barrage"])
                        self.attack_timer = now
                        self.attack_rotation = 0


                elif self.state == "attacking":
                    if self.attack_type == "spiral":
                        self.spiral_attack(now)
                    elif self.attack_type == "barrage":
                        self.barrage_attack(now)

            else:
                # Normal enemy
                self.x += dx * self.speed * speed_multiplier
                self.y += dy * self.speed * speed_multiplier

        # Burning damage over time
        if "burn" in self.status_effects:
            b = self.status_effects["burn"]
            if now - b["time"] < b["duration"]:
                if now >= b["next_tick"]:
                    burn_damage = calculate_sword_damage() * 0.1
                    self.hp -= burn_damage
                    self.trigger_flash((255, 120, 0))
                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, burn_damage))
                    b["next_tick"] = now + b["tick"]
            else:
                del self.status_effects["burn"]

        # Poison damage over time
        if "poison" in self.status_effects:
            p = self.status_effects["poison"]
            if now - p["time"] < p["duration"]:
                if now >= p["next_tick"]:
                    poison_damage = calculate_sword_damage() * 0.3
                    self.hp -= poison_damage
                    self.trigger_flash((0, 255, 0))
                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, poison_damage))
                    p["next_tick"] = now + p["tick"]
            else:
                del self.status_effects["poison"]

    def spiral_attack(self, now):
        if now - self.attack_timer < 3000:
            if (now - self.attack_timer) % 100 < 30:
                for offset in (0, math.pi):
                    angle = math.radians(self.attack_rotation) + offset
                    rockets.append(BossRocket(self.x, self.y, angle))
            self.attack_rotation += 3
        else:
            self.state = "moving"
            self.next_move_time = pygame.time.get_ticks() + 2000  # Longer idle after attack



    def barrage_attack(self, now):
        if now - self.attack_timer < 3000:
            if (now - self.attack_timer) % 300 < 30:
                dx = player_x - self.x
                dy = player_y - self.y
                angle = math.atan2(dy, dx)
                rockets.append(BossRocket(self.x, self.y, angle))
        else:
            self.state = "moving"
            self.next_move_time = pygame.time.get_ticks() + 2000





    def take_damage(self, damage, player_x, player_y):
        self.hp -= damage
        if self.hp > 0:
            global score

            dx = self.x - player_x
            dy = self.y - player_y
            distance = math.hypot(dx, dy)
            if distance != 0:
                self.knockback_direction = (dx / distance, dy / distance)
            self.knockback = 10

            # Knockback multiplier
            if self.type == "harpooner" and self.latched:
                multiplier = 2.5
            elif "knockback effect on enemies 2x" in current_sword.major_affixes:
                multiplier = 1.5
            else:
                multiplier = 1.0

            self.knockback_velocity = 10 * multiplier
            self.knockback_velocity = min(self.knockback_velocity, 15)

            self.trigger_flash((255, 255, 255))

            # Special: Teleporter chance to teleport when hit
            if self.type == "teleporter":
                if random.random() < 0.75:
                    # Teleport opposite of sword direction
                    teleport_distance = random.randint(100,300)

                    # Calculate sword direction
                    mx, my = pygame.mouse.get_pos()
                    sword_angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)

                    teleport_angle = sword_angle + math.pi  # opposite direction

                    old_x, old_y = self.x, self.y
                    self.x = player_x + math.cos(teleport_angle) * teleport_distance
                    self.y = player_y + math.sin(teleport_angle) * teleport_distance

                    # Purple teleport particles
                    for _ in range(15):
                        particles.append(Particle(
                            old_x + random.randint(-10, 10),
                            old_y + random.randint(-10, 10),
                            (150, 0, 255),
                            behavior="teleport"
                        ))
                    
                    for _ in range(15):
                        particles.append(Particle(
                            self.x + random.randint(-10, 10),
                            self.y + random.randint(-10, 10),
                            (150, 0, 255),
                            behavior="teleport"
                        ))
        else:
            if self.hp <= 0:
                global score
                if self.type == "rocketeer":
                    score += 8
                elif self.type == "harpooner":
                    score += 7
                elif self.type == "teleporter":
                    score += 8
                elif self.type == "conjivictus":
                    score += 200
                else:
                    score += 5


        # Damage number




    def draw(self):
        now = pygame.time.get_ticks()

        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)

        if self.flash_color and now - self.flash_time < self.flash_duration:
            draw_color = self.flash_color
        else:
            draw_color = self.color if isinstance(self.color, list) else self.color

        if self.type == "rocketeer":
            elapsed = now - self.last_shot_time
            charging_time = 800
            charging = min(elapsed / charging_time, 1.0)

            if not self.flash_color:
                draw_color = [min(255, int(c * (1 + 0.5 * charging))) for c in self.base_color]

            pygame.draw.circle(screen, draw_color, (draw_x, draw_y), self.size)

            scale_factor = (self.size * 3.5) / 90
            scaled_spike = pygame.transform.scale(rocket_spike_image, (int(90 * scale_factor), int(90 * scale_factor)))
            rect = scaled_spike.get_rect(center=(draw_x, draw_y))
            screen.blit(scaled_spike, rect.topleft)

        elif self.type == "harpooner":
            pygame.draw.circle(screen, draw_color, (draw_x, draw_y), self.size)

            scale_factor = (self.size * 3.5) / 90
            scaled_hat = pygame.transform.scale(harpooner_hat_image, (int(90 * scale_factor), int(90 * scale_factor)))
            rect = scaled_hat.get_rect(center=(draw_x, draw_y))
            screen.blit(scaled_hat, rect.topleft)

            if self.harpoon_state in ("shooting", "returning", "pulling"):
                harpoon_draw_x = int(self.harpoon_pos[0] - camera_x + WIDTH // 2)
                harpoon_draw_y = int(self.harpoon_pos[1] - camera_y + HEIGHT // 2)
                pygame.draw.line(screen, (255, 255, 255), (draw_x, draw_y), (harpoon_draw_x, harpoon_draw_y), 4)

        elif self.type == "teleporter":
            pygame.draw.circle(screen, draw_color, (draw_x, draw_y), self.size)

            scale_factor = (self.size * 3.5) / 90
            scaled_hat = pygame.transform.scale(teleporter_hat_image, (int(90 * scale_factor), int(90 * scale_factor)))
            rect = scaled_hat.get_rect(center=(draw_x, draw_y))
            screen.blit(scaled_hat, rect.topleft)

        elif self.type == "conjivictus":
            sprite = pygame.transform.scale(pygame.image.load("conjivictus.png"), (self.size*2, self.size*2))
            rect = sprite.get_rect(center=(draw_x, draw_y))
            screen.blit(sprite, rect.topleft)

            if self.attack_type == "madness":
                for zone in self.zones:
                    zone.draw()


        else:
            # Normal enemy
            pygame.draw.circle(screen, draw_color, (draw_x, draw_y), self.size)


    def is_alive(self):
        return self.hp > 0

class BossRocket:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 4000  # 4 seconds
        self.damage = 30
        self.explosion_radius = 100
        self.image = pygame.transform.scale(pygame.image.load("con_rocket.png"), (80, 40))
        self.last_trail_time = pygame.time.get_ticks()

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        now = pygame.time.get_ticks()

        # Particle trail every 50ms
        if now - self.last_trail_time > 50:
            self.last_trail_time = now
            particles.append(Particle(self.x, self.y, (255, 100, 255)))

        # Collision with player
        if math.hypot(player_x - self.x, player_y - self.y) < self.explosion_radius:
            self.explode()

        # Timeout explosion
        if now - self.spawn_time > self.lifetime:
            self.explode()

    def explode(self):
        global player_health
        if math.hypot(player_x - self.x, player_y - self.y) < self.explosion_radius:
            player_health -= self.damage
            camera_shake_intensity = 15  # set initial shake strength

            damage_flash_time = pygame.time.get_ticks()


        # Explosion particles (scatter manually)
        for _ in range(10):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            particle = Particle(self.x + offset_x, self.y + offset_y, (255, 100, 255))
            particles.append(particle)

        try:
            rockets.remove(self)
        except ValueError:
            pass

    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated, rect.topleft)


class ExplodingZone:
    def __init__(self, x, y, bigger=False):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.size = 80 if not bigger else 150
        self.charge_time = 2000  # brightening lasts 2 seconds
        self.wait_time = 1000    # wait 1 second before starting brightening
        self.exploded = False
        self.ready = False

    def update(self, now):
        elapsed = now - self.start_time

        if not self.ready and elapsed >= self.wait_time:
            self.ready = True
            self.start_charging_time = now

        if self.ready:
            charge_elapsed = now - self.start_charging_time

            if charge_elapsed >= self.charge_time:
                self.explode()
        
    def explode(self):
        self.exploded = True
        global player_health
        if math.hypot(player_x - self.x, player_y - self.y) < self.size:
            player_health -= 30
            camera_shake_intensity = 15  # set initial shake strength

            damage_flash_time = pygame.time.get_ticks()


    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)

        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        # Load and scale the zone texture
        base_image = pygame.image.load("zone.png").convert_alpha()
        scaled_image = pygame.transform.scale(base_image, (self.size * 2, self.size * 2))

        # Calculate alpha transparency
        if not self.ready:
            alpha = 100  # Dim at first
        else:
            charge_elapsed = now - self.start_charging_time
            alpha = min(255, int(100 + 155 * (charge_elapsed / self.charge_time)))

        # Create temporary surface to adjust brightness
        temp_surface = scaled_image.copy()
        temp_surface.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw to screen
        screen.blit(temp_surface, (draw_x - self.size, draw_y - self.size))

class Rocket:
    def __init__(self, x, y, angle, boss=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 6000  # Explode after 6 seconds
        self.explosion_radius = 120
        self.damage = 30
        if boss:
            self.image = pygame.transform.scale(pygame.image.load("con_rocket.png"), (80, 40))
        else:
            self.image = pygame.transform.scale(pygame.image.load("rocket.png"), (60, 30))

    def update(self):
        # Slightly home toward the player
        dx = player_x - self.x
        dy = player_y - self.y
        target_angle = math.atan2(dy, dx)

        diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += diff * 0.05

        # Move forward
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Explosion if near player
        if math.hypot(self.x - player_x, self.y - player_y) < 30:
            camera_shake_intensity = 15
            damage_flash_time = pygame.time.get_ticks()

            self.explode()
            return

        # Explosion after timeout
        now = pygame.time.get_ticks()
        if now - self.spawn_time > 4000:
            self.explode()

    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated, rect.topleft)

    def explode(self):
        global camera_shake_intensity, damage_flash_time

        dist = math.hypot(player_x - self.x, player_y - self.y)
        if dist < self.explosion_radius:
            global player_health, player_knockback, player_knockback_velocity, player_knockback_direction
            player_health -= self.damage
            camera_shake_intensity = 15  # set initial shake strength

            damage_flash_time = pygame.time.get_ticks()

            dx = player_x - self.x
            dy = player_y - self.y
            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                player_knockback_direction = (dx / length, dy / length)
                player_knockback = 1
                player_knockback_velocity = 15

        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            p = Particle(self.x, self.y, (255, 100, 0))
            p.vx = math.cos(angle) * speed
            p.vy = math.sin(angle) * speed
            particles.append(p)

        if self in rockets:
            rockets.remove(self)

    def draw(self):
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated, rect.topleft)


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
            self.vy -= 0.1
            self.vx += random.uniform(-0.3, 0.3)
        elif self.behavior == "poison":
            self.vx += random.uniform(-0.3, 0.3)
            self.vy += random.uniform(-0.3, 0.3)

        self.x += self.vx
        self.y += self.vy

        # ❗ Dodamo upočasnjevanje
        self.vx *= 0.96
        self.vy *= 0.96

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
        self.amount = f"{amount:.1f}".rstrip('0').rstrip('.')  # removes trailing .0
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

spawn_chest_timer = 0
spawn_chest_interval = 3000  # every 10 seconds

spawn_scroll_timer = 0
spawn_scroll_interval = 2000  # milliseconds (spawn a scroll every 5 seconds)

enemy_spawn_time = 3000
last_spawn_time = 0
enemies = []
rockets = []

particles = []
damage_numbers = []

def draw_walls():
    wall_thickness = 20
    map_min = -2100
    map_max = 2100

    # Calculate wall positions relative to camera
    top_left_x = map_min - camera_x + WIDTH // 2 + int(world_offset_x)
    top_left_y = map_min - camera_y + HEIGHT // 2 + int(world_offset_y)
    bottom_right_x = map_max - camera_x + WIDTH // 2 + int(world_offset_x)
    bottom_right_y = map_max - camera_y + HEIGHT // 2 + int(world_offset_y)

    # Top wall
    pygame.draw.rect(screen, (255, 0, 0), (top_left_x, top_left_y - wall_thickness, bottom_right_x - top_left_x, wall_thickness))
    # Bottom wall
    pygame.draw.rect(screen, (255, 0, 0), (top_left_x, bottom_right_y, bottom_right_x - top_left_x, wall_thickness))
    # Left wall
    pygame.draw.rect(screen, (255, 0, 0), (top_left_x - wall_thickness, top_left_y, wall_thickness, bottom_right_y - top_left_y))
    # Right wall
    pygame.draw.rect(screen, (255, 0, 0), (bottom_right_x, top_left_y, wall_thickness, bottom_right_y - top_left_y))


def spawn_enemy():
    enemies.append(Enemy(enemy_type="normal"))

def spawn_rocketeer():
    enemies.append(Enemy(enemy_type="rocketeer"))

def spawn_harpooner():
    enemies.append(Enemy(enemy_type="harpooner"))

def spawn_teleporter():
    enemies.append(Enemy(enemy_type="teleporter"))

def spawn_boss_conjivictus():

    e = Enemy(enemy_type="conjivictus")
#    e.x = random.randint(-1000, 1000)
#    e.y = random.randint(-1000, 1000)
    e.x = 200
    e.y = 200
    enemies.append(e)



def handle_movement(keys):
    global player_x, player_y
    if player_knockback == 0:
        if keys[pygame.K_w] and player_y - player_speed > -2100: player_y -= player_speed
        if keys[pygame.K_s] and player_y + player_speed < 2100: player_y += player_speed
        if keys[pygame.K_a] and player_x - player_speed > -2100: player_x -= player_speed
        if keys[pygame.K_d] and player_x + player_speed < 2100: player_x += player_speed


MINOR_LINE_HEIGHT = 22
MAJOR_LINE_HEIGHT = 22
LEGENDARY_LINE_HEIGHT = 22
        
# --- NOVI DELI KODE ZA MEČE NA MAPI ---
class SwordPickup:
    def __init__(self, x, y, sword):
        self.spawn_time = pygame.time.get_ticks()
        self.alive = True

        self.x = x
        self.y = y
        self.sword = sword
        self.size = 48  # velikost kvadrata

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > 10000:  # 10 seconds
            self.alive = False


    def draw(self):
        color = sword_colors[self.sword.sword_type]
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        img = pygame.image.load(self.sword.sword_texture).convert_alpha()

    # Elongated before rotating
        long_sword_width = 100  # try 100-120 for length
        long_sword_height = 30  # keep it slim

        img = pygame.transform.scale(img, (long_sword_width, long_sword_height))
        img = pygame.transform.rotate(img, 45)

        screen.blit(img, (draw_x - self.size // 2, draw_y - self.size // 2))
        if not self.sword:
            return

        # Prikaz statov če je igralec blizu
        if math.hypot(player_x - self.x, player_y - self.y) < 100:
            font = pygame.font.SysFont(None, 28)
            gear_text = f"{self.sword.sword_name} {Sword.roman_levels[self.sword.gear_level - 1]} Sword"


            if self.sword.major_affixes:
                gear_text += " *"
            if self.sword.is_legendary:
                gear_text += " L"
                name_color = (255, 215, 0)
            else:
                name_color = sword_colors[self.sword.sword_type]

            lines = [
                (gear_text, name_color),
                ("Damage: " + str(self.sword.base_damage), (255, 255, 255)),
            ]

            for i, (text, color) in enumerate(lines):
                rendered = font.render(text, True, color)
                screen.blit(rendered, (draw_x + 50, draw_y + i * 22 - 10))

            # Effects header
                effect_font = pygame.font.SysFont(None, 24)
                screen.blit(effect_font.render("Effects:", True, (255, 255, 255)), (draw_x + 50, draw_y + 50))
                y_offset = draw_y + 70

            # Minor affixes (green)
            minor_font = pygame.font.SysFont(None, 22)
            for affix in self.sword.minor_affixes:
                screen.blit(minor_font.render("-  " + affix, True, (0, 255, 100)), (draw_x + 50, y_offset))
                y_offset += MINOR_LINE_HEIGHT

            # Major affixes (white)
            for affix in self.sword.major_affixes:
                 y_offset = draw_wrapped_text(screen, f"- {affix}", effect_font, (255, 255, 255), draw_x + 50, y_offset, 400, MAJOR_LINE_HEIGHT)

            # Legendary affixes (yellow, bigger)
            legend_font = pygame.font.SysFont(None, 26, bold=True)
            for affix in self.sword.legendary_affixes:
                y_offset = draw_wrapped_text(screen, f"- {affix}", legend_font, (255, 255, 0), draw_x + 50, y_offset, 400, LEGENDARY_LINE_HEIGHT)

    def is_near_player(self):
        return math.hypot(player_x - self.x, player_y - self.y) < 100

# Seznam mečev na mapi
sword_pickups = []

def spawn_sword_pickup():
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    sword = Sword()
    sword.gear_level = random.randint(1, 7)
    sword.base_damage = random.randint(5 + 2 * sword.gear_level, 10 + 3 * sword.gear_level)
    sword.sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])
    sword.is_legendary = random.random() < 0.05

    if sword.is_legendary:
        sword.major_affixes = random.sample(Sword.major_pool, k=random.randint(1, 3))
        sword.legendary_affixes = random.sample(Sword.legendary_pool, k=random.randint(1, 2))
    else:
        sword.minor_affixes = random.sample(Sword.minor_pool, k=random.randint(1, sword.gear_level))
        if random.random() < 0.3:
            sword.major_affixes = [random.choice(Sword.major_pool)]

    sword_pickups.append(SwordPickup(x, y, sword))

# Flag za prikaz UI za zamenjavo
selecting_sword = False
new_sword_candidate = None

inventory_open = False
chest_sword_boxes = []

def draw_sword_box(x, y, sword, title):
    rect = pygame.Rect(x, y, 360, 600)
    hover = rect.collidepoint(pygame.mouse.get_pos()) and selecting_sword and title != "New Sword"
    if hover:
        border_color = (255, 255, 255)  # White outline
    else:
        border_color = (255, 215, 0) if getattr(sword, 'is_legendary', False) else sword_colors.get(getattr(sword, 'sword_type', ""), (255, 255, 255))

    # Gradient background
    gradient_surface = pygame.Surface((rect.width, rect.height))
    if getattr(sword, 'is_legendary', False):
        background_color = (255, 215, 0)
    else:
        background_color = sword_colors.get(getattr(sword, 'sword_type', ""), (80, 80, 80))

    base_color = pygame.Color(
        int(background_color[0] * 0.3),
        int(background_color[1] * 0.3),
        int(background_color[2] * 0.3)
    )

    for i in range(rect.height):
        color = base_color.lerp((15, 15, 15), i / rect.height * 0.6)
        pygame.draw.line(gradient_surface, color, (0, i), (rect.width, i))
    screen.blit(gradient_surface, (x, y))

    # Border
    pygame.draw.rect(screen, border_color, rect, 4)

    # Sword image
    sword_name = getattr(sword, 'sword_name', None)
    if sword_name in sword_images:
        img = sword_images[sword_name]
        img = pygame.transform.scale(img, (80, 40))
        img = pygame.transform.rotate(img, 45)
        img_rect = img.get_rect(topright=(x + rect.width - 10, y + 10))
        screen.blit(img, img_rect)


    font = pygame.font.SysFont(None, 24)
    bold_font = pygame.font.SysFont(None, 24, bold=True)
    big_font = pygame.font.SysFont(None, 28)
    legendary_font = pygame.font.SysFont(None, 28, bold=True)

    # Title with gear level
    gear_text = f"{sword_name.capitalize()} Sword {Sword.roman_levels[getattr(sword, 'gear_level', 1) - 1]}" if sword_name else "Unknown Item"
    if getattr(sword, 'is_legendary', False):
        gear_text = gear_text.upper() + " L"
        title_color = (255, 215, 0)
    else:
        title_color = border_color

    if getattr(sword, 'major_affixes', []):
        gear_text += " *"

    screen.blit(bold_font.render(title, True, title_color), (x + 15, y + 12))
    screen.blit(big_font.render(gear_text, True, title_color), (x + 15, y + 38))

    y_offset = y + 100

    # Damage
    if isinstance(sword, Sword):
        scaled_damage = int(sword.get_damage(player_brutality, player_tactics, player_survival))
        screen.blit(font.render("Total Damage:", True, (230, 230, 230)), (x + 15, y + 64))
        screen.blit(font.render(str(scaled_damage), True, title_color), (x + 150, y + 64))
    else:

        screen.blit(font.render("No Damage", True, (230, 230, 230)), (x + 15, y + 64))

    # Effects
    screen.blit(font.render("Effects:", True, (255, 255, 255)), (x + 15, y_offset))
    y_offset += 25

    # Basic effects (for swords)
    if isinstance(sword, Sword):
        for effect in sword.effects:
            effect_name = effect.replace("_", " ").capitalize()
            color = {
                "double crit": (255, 255, 0),
                "freeze": (0, 100, 255),
                "slowness": (128, 128, 128),
                "burn": (255, 100, 0),
                "poison": (0, 255, 0),
            }.get(effect, (255, 255, 255))
            screen.blit(font.render(f"- {effect_name}", True, color), (x + 25, y_offset))
            y_offset += 16

        # Minor affixes (green)
        minor_font = pygame.font.SysFont(None, 22)
        for affix in sword.minor_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", minor_font, (0, 255, 100), x + 25, y_offset, 310, 20)

        # Major affixes (white)
        for affix in sword.major_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", font, (255, 255, 255), x + 25, y_offset, 310, 22)

        # Legendary affixes (yellow, bigger)
        for affix in sword.legendary_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", legendary_font, (255, 255, 0), x + 25, y_offset, 310, 24)

    return rect

def draw_ability_box(x, y, ability, title):
    rect = pygame.Rect(x, y, 360, 600)


    bold_font = pygame.font.SysFont(None, 24, bold=True)
    big_font = pygame.font.SysFont(None, 20)

    # 🛡 SAFELY define title_color immediately
    title_color = (255, 255, 255)

    if ability:
        attr_color = sword_colors.get(ability.ability_type_attr, (255, 255, 255))
        title_color = attr_color

        if ability.is_legendary:
            title_color = (255, 215, 0)

    # draw box background
    pygame.draw.rect(screen, (40, 40, 40), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 4)

    # draw title
    screen.blit(bold_font.render(title, True, title_color), (x + 15, y + 12))

    if not ability:
        font = pygame.font.SysFont(None, 28)
        screen.blit(font.render("Empty Ability", True, (180, 180, 180)), (x + 15, y + 45))
        return rect

    # ... rest of the ability box drawing code ...



    # Determine colors
    is_legendary = ability.is_legendary
    attr_color = sword_colors.get(ability.ability_type_attr, (60, 60, 60))
    mouse_pos = pygame.mouse.get_pos()
    hover = rect.collidepoint(mouse_pos) and selecting_ability

    if hover:
        border_color = (255, 255, 255)  # highlight white
    elif is_legendary:
        border_color = (255, 215, 0)  # gold
    else:
        border_color = attr_color  # base attribute color

    # Gradient background
    gradient_surface = pygame.Surface((rect.width, rect.height))
    base_color = pygame.Color(
        int(attr_color[0] * 0.3),
        int(attr_color[1] * 0.3),
        int(attr_color[2] * 0.3)
    )
    for i in range(rect.height):
        color = base_color.lerp((15, 15, 15), i / rect.height * 0.6)
        pygame.draw.line(gradient_surface, color, (0, i), (rect.width, i))
    screen.blit(gradient_surface, (x, y))

    # Border
    pygame.draw.rect(screen, border_color, rect, 4)

    # Icon
    icon = get_ability_icon(ability.ability_type)
    if icon:
        icon = pygame.transform.scale(icon, (80, 80))
        icon_rect = icon.get_rect(topright=(x + rect.width - 10, y + 10))
        screen.blit(icon, icon_rect)

    # Fonts
    font = pygame.font.SysFont(None, 24)
    bold_font = pygame.font.SysFont(None, 24, bold=True)
    big_font = pygame.font.SysFont(None, 28)
    legendary_font = pygame.font.SysFont(None, 28, bold=True)

    # Title + Gear Level
    # Corrected title and level
    gear_text = f"{ability.name} {Ability.roman_levels[ability.gear_level - 1]}"
    if ability.major_affixes:
        gear_text += " *"
    if is_legendary:
        gear_text += " L"
    else:
        title_color = border_color

    # Draw corrected name + level
    screen.blit(bold_font.render(title, True, title_color), (x + 15, y + 12))  # Title: "Current Ability" or "New Ability"
    screen.blit(big_font.render(gear_text, True, title_color), (x + 15, y + 38))


    y_offset = y + 100

    # ➡️ Show damage or special info
    damage_font = pygame.font.SysFont(None, 24)

    if ability.ability_type == AbilityType.BURN:
        burn_damage = int(ability.base_damage)
        ticks = 3
        screen.blit(damage_font.render(f"Damage: {burn_damage} × {ticks}", True, (255, 140, 0)), (x + 15, y_offset))
        y_offset += 25
    elif ability.ability_type == AbilityType.FREEZE:
        freeze_time = 2.0
        screen.blit(damage_font.render(f"Freeze Time: {freeze_time:.1f}s", True, (100, 150, 255)), (x + 15, y_offset))
        y_offset += 25
    elif ability.ability_type == AbilityType.SCATTER_BOMB:
        mini_damage = int(ability.base_damage)
        screen.blit(damage_font.render(f"Mini Bomb: {mini_damage} × 4", True, (255, 255, 255)), (x + 15, y_offset))
        y_offset += 25
    else:
        screen.blit(damage_font.render(f"Damage: {int(ability.base_damage)}", True, (255, 255, 255)), (x + 15, y_offset))
        y_offset += 25

    # ➡️ Show cooldown
    screen.blit(damage_font.render(f"Cooldown: {ability.cooldown/1000:.1f}s", True, (200, 200, 200)), (x + 15, y_offset))
    y_offset += 30


    # Minor affixes (green)
    minor_font = pygame.font.SysFont(None, 22)
    for affix in ability.minor_affixes:
        y_offset = draw_wrapped_text(screen, f"- {affix}", minor_font, (0, 255, 100), x + 25, y_offset, 310, 20)

    # Major affixes (white)
    for affix in ability.major_affixes:
        y_offset = draw_wrapped_text(screen, f"- {affix}", font, (255, 255, 255), x + 25, y_offset, 310, 22)

    # Legendary affixes (yellow, bigger)
    for affix in ability.legendary_affixes:
        y_offset = draw_wrapped_text(screen, f"- {affix}", legendary_font, (255, 255, 0), x + 25, y_offset, 310, 24)

    return rect




class AbilityPickup:
    def __init__(self, x, y, ability):
        self.spawn_time = pygame.time.get_ticks()
        self.alive = True

        self.x = x
        self.y = y
        self.ability = ability
        self.size = 48  # icon size

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > 10000:  # 10 seconds
            self.alive = False



    def draw(self):
        if not self.ability:
            return

        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)

        # Draw ability icon only (no colored square behind)
        icon = get_ability_icon(self.ability.ability_type)
        if icon:
            icon_scaled = pygame.transform.scale(icon, (self.size, self.size))
            screen.blit(icon_scaled, (draw_x - self.size // 2, draw_y - self.size // 2))

        # Show detailed info if player is near
        if self.is_near_player():
            font = pygame.font.SysFont(None, 28)
            attr_color = sword_colors.get(self.ability.ability_type_attr, (255, 255, 255))
            gear_text = f"{self.ability.ability_type_attr.capitalize()} Ability {Ability.roman_levels[self.ability.gear_level - 1]}"
            if self.ability.major_affixes:
                gear_text += " *"
            if self.ability.is_legendary:
                gear_text += " L"
                name_color = (255, 215, 0)
            else:
                name_color = attr_color

            # Show name and description
            lines = [
                (f"{self.ability.name} {gear_text}", name_color),
            ]

            # ➡️ ADD THIS after existing two lines
            # ➡️ Add damage or special info
            if self.ability.ability_type == AbilityType.BURN:
                burn_damage = int(self.ability.base_damage)  # or apply scaling here later
                ticks = 3  # or however many ticks your Burn applies (example 3)
                lines.append((f"Damage: {burn_damage} × {ticks}", (255, 140, 0)))
            elif self.ability.ability_type == AbilityType.FREEZE:
                freeze_time = 2.0  # seconds or whatever your freeze duration is (example)
                lines.append((f"Freeze Time: {freeze_time:.1f}s", (100, 150, 255)))
            elif self.ability.ability_type == AbilityType.SCATTER_BOMB:
                mini_damage = int(self.ability.base_damage)  # small bombs base damage
                lines.append((f"Mini Bomb: {mini_damage} × 4", (255, 255, 255)))
            else:
                lines.append((f"Damage: {int(self.ability.base_damage)}", (255, 255, 255)))

            cooldown_sec = self.ability.cooldown / 1000
            lines.append((f"Cooldown: {self.ability.cooldown/1000:.1f}s", (200, 200, 200)))


  
            for i, (text, color) in enumerate(lines):
                rendered = font.render(text, True, color)
                screen.blit(rendered, (draw_x + 50, draw_y + i * 22 - 10))

            # Effects header
            y_offset = draw_y + (len(lines) * 22) + 10
            screen.blit(font.render("Effects:", True, (255, 255, 255)), (draw_x + 50, y_offset))
            y_offset += 25

            # Minor affixes
            minor_font = pygame.font.SysFont(None, 22)
            for affix in self.ability.minor_affixes:
                screen.blit(minor_font.render("-  " + affix, True, (0, 255, 100)), (draw_x + 50, y_offset))
                y_offset += MINOR_LINE_HEIGHT

            # Major affixes
            for affix in self.ability.major_affixes:
                y_offset = draw_wrapped_text(screen, f"- {affix}", font, (255, 255, 255), draw_x + 50, y_offset, 400, MAJOR_LINE_HEIGHT)

            # Legendary affixes
            legend_font = pygame.font.SysFont(None, 26, bold=True)
            for affix in self.ability.legendary_affixes:
                y_offset = draw_wrapped_text(screen, f"- {affix}", legend_font, (255, 255, 0), draw_x + 50, y_offset, 400, LEGENDARY_LINE_HEIGHT)

    def is_near_player(self):
        return math.hypot(player_x - self.x, player_y - self.y) < 100


ability_pickups = []

def draw_sword_swap_ui():
    global sword_box1, sword_box2, sword_box3

    # Title
    title_font = pygame.font.SysFont(None, 60)
    title_text = title_font.render("Swap Item", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Move Slot 1 and Slot 2 more left
    sword_box1 = draw_sword_box(WIDTH // 2 - 650, 300, sword_1, "Sword 1")
    sword_box2 = draw_sword_box(WIDTH // 2 - 250, 300, sword_2, "Sword 2")
    sword_box3 = draw_sword_box(WIDTH // 2 + 400, 300, new_sword_candidate, "New Sword")

    # Labels
    small_font = pygame.font.SysFont(None, 36)
    label1 = small_font.render("Slot 1", True, (255, 255, 255))
    label2 = small_font.render("Slot 2", True, (255, 255, 255))
    label3 = small_font.render("New Item", True, (255, 255, 255))
    screen.blit(label1, (sword_box1.centerx - label1.get_width() // 2, sword_box1.top - 40))
    screen.blit(label2, (sword_box2.centerx - label2.get_width() // 2, sword_box2.top - 40))
    screen.blit(label3, (sword_box3.centerx - label3.get_width() // 2, sword_box3.top - 40))



def draw_ability_swap_ui():
    global sword_box3, sword_box4, sword_box5

    # Title
    title_font = pygame.font.SysFont(None, 60)
    title_text = title_font.render("Swap Item", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Move Slot 1 and Slot 2 more left
    sword_box3 = draw_ability_box(WIDTH // 2 - 650, 300, player_ability_1, "Ability 1")
    sword_box4 = draw_ability_box(WIDTH // 2 - 250, 300, player_ability_2, "Ability 2")
    sword_box5 = draw_ability_box(WIDTH // 2 + 400, 300, new_sword_candidate, "New Ability")

    # Labels
    small_font = pygame.font.SysFont(None, 36)
    label1 = small_font.render("Slot 1", True, (255, 255, 255))
    label2 = small_font.render("Slot 2", True, (255, 255, 255))
    label3 = small_font.render("New Item", True, (255, 255, 255))
    screen.blit(label1, (sword_box3.centerx - label1.get_width() // 2, sword_box3.top - 40))
    screen.blit(label2, (sword_box4.centerx - label2.get_width() // 2, sword_box4.top - 40))
    screen.blit(label3, (sword_box5.centerx - label3.get_width() // 2, sword_box5.top - 40))

def spawn_ability_pickup():
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    ability_type = random.choice(list(AbilityType))
    ability = Ability(ability_type)
    ability_pickups.append(AbilityPickup(x, y, ability))

def draw_sword_selection_ui():
    global sword_box1, sword_box2, sword_box3, sword_box4
    global chest_sword_boxes

    sword_box1 = None
    sword_box2 = None
    sword_box3 = None
    sword_box4 = None
    chest_sword_boxes = []

    font = pygame.font.SysFont(None, 64)
    if chest_being_opened:
        chest_type_str = "SWORD" if isinstance(chest_being_opened, SwordChest) else "ABILITY"
        chest_name = f"{chest_being_opened.rarity.upper()} {chest_type_str} CHEST"
        text = font.render(chest_name, True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))

        bottom_font = pygame.font.SysFont(None, 48)
        choose_str = "CHOOSE A SWORD" if isinstance(chest_being_opened, SwordChest) else "CHOOSE AN ABILITY"
        choose_text = bottom_font.render(choose_str, True, (255, 255, 255))

        screen.blit(choose_text, (WIDTH//2 - choose_text.get_width()//2, HEIGHT - 100))




    if inventory_open:
        # INVENTORY - showing your 2 swords and 2 abilities
        sword_box1 = draw_sword_box(WIDTH // 2 - 800, 200, sword_1, "Sword 1")
        sword_box2 = draw_sword_box(WIDTH // 2 - 430, 200, sword_2, "Sword 2")
        sword_box3 = draw_ability_box(WIDTH // 2 + 40, 200, player_ability_1, "Ability 1")
        sword_box4 = draw_ability_box(WIDTH // 2 + 410, 200, player_ability_2, "Ability 2")

    if chest_ui_weapons:
        if isinstance(chest_being_opened, AbilityChest):

            # Ability chest
            if len(chest_ui_weapons) > 0:
                chest_sword_boxes.append(draw_ability_box(WIDTH // 2 - 545, 200, chest_ui_weapons[0], "Ability A"))
            if len(chest_ui_weapons) > 1:
                chest_sword_boxes.append(draw_ability_box(WIDTH // 2 - 145, 200, chest_ui_weapons[1], "Ability B"))
            if len(chest_ui_weapons) > 2:
                chest_sword_boxes.append(draw_ability_box(WIDTH // 2 + 245, 200, chest_ui_weapons[2], "Ability C"))
        else:
            # Sword chest
            if len(chest_ui_weapons) > 0:
                chest_sword_boxes.append(draw_sword_box(WIDTH // 2 - 545, 200, chest_ui_weapons[0], "Sword A"))
            if len(chest_ui_weapons) > 1:
                chest_sword_boxes.append(draw_sword_box(WIDTH // 2 - 145, 200, chest_ui_weapons[1], "Sword B"))
            if len(chest_ui_weapons) > 2:
                chest_sword_boxes.append(draw_sword_box(WIDTH // 2 + 245, 200, chest_ui_weapons[2], "Sword C"))



    elif selecting_sword and new_sword_candidate:
        draw_sword_swap_ui()
    elif selecting_ability and new_sword_candidate:
        draw_ability_swap_ui()








    # Draw arrow FROM new sword (sword_box3) TO hovered sword (sword_box1 or 2)
    if selecting_sword and new_sword_candidate and sword_box3:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        hovered_box = None
        if sword_box1 and sword_box1.collidepoint((mouse_x, mouse_y)):
            hovered_box = sword_box1
        elif sword_box2 and sword_box2.collidepoint((mouse_x, mouse_y)):
            hovered_box = sword_box2

        if hovered_box:
            start = (sword_box3.centerx, sword_box3.centery)
            end = (hovered_box.centerx, hovered_box.centery)

            pygame.draw.line(screen, (255, 255, 255), start, end, 4)

            # Draw arrowhead
            angle = math.atan2(end[1] - start[1], end[0] - start[0])
            length = 20
            arrow_tip1 = (
                end[0] - length * math.cos(angle - math.pi / 6),
                end[1] - length * math.sin(angle - math.pi / 6)
            )
            arrow_tip2 = (
                end[0] - length * math.cos(angle + math.pi / 6),
                end[1] - length * math.sin(angle + math.pi / 6)
            )
            pygame.draw.polygon(screen, (255, 255, 255), [end, arrow_tip1, arrow_tip2])






def handle_sword_pickup_events(events):
    global player_ability_1, player_ability_2
    global selecting_sword, selecting_ability, new_sword_candidate
    global sword_pickups, ability_pickups
    global sword_1, sword_2, inventory_open
    global chest_ui_weapons, chest_being_opened

    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and not (selecting_sword or selecting_ability) and not inventory_open:
                # Check for nearby sword pickups
                for pickup in sword_pickups:
                    if pickup.is_near_player():
                        selecting_sword = True
                        new_sword_candidate = pickup.sword
                        sword_pickups.remove(pickup)
                        break
                # Check for nearby ability pickups
                for pickup in ability_pickups:
                    if pickup.is_near_player():
                        selecting_ability = True
                        new_sword_candidate = pickup.ability
                        ability_pickups.remove(pickup)
                        break

            elif event.key == pygame.K_g or event.key == pygame.K_TAB:
                # Cancel pickup and drop the item back
                if selecting_sword and new_sword_candidate:
                    sword_pickups.append(SwordPickup(player_x, player_y, new_sword_candidate))
                    selecting_sword = False
                    new_sword_candidate = None
                elif selecting_ability and new_sword_candidate:
                    ability_pickups.append(AbilityPickup(player_x, player_y, new_sword_candidate))
                    selecting_ability = False
                    new_sword_candidate = None
                else:
                    inventory_open = not inventory_open

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if chest_ui_weapons:
                for idx, box in enumerate(chest_sword_boxes):
                    if isinstance(box, pygame.Rect) and box.collidepoint(mouse_x, mouse_y):
                        selected = chest_ui_weapons[idx]

                        drop_x = chest_being_opened.x
                        drop_y = chest_being_opened.y

                        if isinstance(selected, Sword):
                            sword_pickups.append(SwordPickup(drop_x, drop_y, selected))
                        elif isinstance(selected, Ability):
                            ability_pickups.append(AbilityPickup(drop_x, drop_y, selected))

                        # Close chest UI
                        chest_ui_weapons = []
                        if chest_being_opened in chests:
                            chests.remove(chest_being_opened)
                            chest_being_opened = None

                        selecting_sword = False
                        selecting_ability = False
                        new_sword_candidate = None
                        break

            elif selecting_sword and new_sword_candidate:
                if sword_box1 and sword_box1.collidepoint(mouse_x, mouse_y):
                    if sword_1 is not None:
                        sword_pickups.append(SwordPickup(player_x, player_y, sword_1))
                    sword_1 = new_sword_candidate
                    selecting_sword = False
                    new_sword_candidate = None


                    if chest_being_opened:
                        if chest_being_opened in chests:
                            chests.remove(chest_being_opened)
                        chest_being_opened = None
                                            
                elif sword_box2 and sword_box2.collidepoint(mouse_x, mouse_y):
                    if sword_2 is not None:
                        sword_pickups.append(SwordPickup(player_x, player_y, sword_2))
                    sword_2 = new_sword_candidate
                    selecting_sword = False
                    new_sword_candidate = None

                                
                    if chest_being_opened:
                        if chest_being_opened in chests:
                            chests.remove(chest_being_opened)
                        chest_being_opened = None

            elif selecting_ability and new_sword_candidate:
                if sword_box3 and sword_box3.collidepoint(mouse_x, mouse_y):
                    ability_pickups.append(AbilityPickup(player_x, player_y, player_ability_1))
                    player_ability_1 = new_sword_candidate
                    selecting_ability = False
                    new_sword_candidate = None
                elif sword_box4 and sword_box4.collidepoint(mouse_x, mouse_y):
                    ability_pickups.append(AbilityPickup(player_x, player_y, player_ability_2))
                    player_ability_2 = new_sword_candidate
                    selecting_ability = False
                    new_sword_candidate = None

def update_sword(player_draw_x, player_draw_y):
    global player_health
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

    image = sword_images[current_sword.sword_name]


    sword_image = pygame.transform.scale(image, (120, 60))
    sword_rotated = pygame.transform.rotate(sword_image, math.degrees(angle + 80))


    sword_rect = sword_rotated.get_rect(
        center=(player_draw_x + math.sin(angle) * (80 + thrust_distance),
                player_draw_y + math.cos(angle) * (80 + thrust_distance))
    )
    screen.blit(sword_rotated, sword_rect.topleft)

    if sword_thrust and thrust_velocity > 0:

        for enemy in enemies:
            enemy_rect = pygame.Rect(
                int(enemy.x - camera_x + WIDTH // 2 - enemy.size),
                int(enemy.y - camera_y + HEIGHT // 2 - enemy.size),
                enemy.size * 2, enemy.size * 2
            )

            if sword_rect.colliderect(enemy_rect) and enemy.id not in sword_hit_enemies:
                crit = is_critical_hit()
                damage = calculate_sword_damage() * (2 if crit else 1)
                enemy.take_damage(damage, player_x, player_y)
                if "1% of HP recovered per attack" in current_sword.major_affixes:
                    player_health += max_health * 0.01
                    if player_health > max_health:
                        player_health = max_health

                enemy.trigger_flash((255, 255, 255))  # white flash
                damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage, critical=crit))
                sword_hit_enemies.add(enemy.id)

                # Major affixes (on hit)
                if "poisons enemy" in current_sword.major_affixes:
                    duration = 6000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["poison"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": duration,
                        "tick": 1000,
                        "next_tick": pygame.time.get_ticks() + 1000,
                    }

                if "burns enemy" in current_sword.major_affixes:
                    duration = 3000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["burn"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": duration,
                        "tick": 300,
                        "next_tick": pygame.time.get_ticks() + 300,
                    }

                if "freezes enemy" in current_sword.major_affixes:
                    duration = 1000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["freeze"] = {"time": pygame.time.get_ticks(), "duration": duration}

                if "slows enemy" in current_sword.major_affixes:
                    duration = 2000 * (1.1 ** get_attribute_level())
                    enemy.status_effects["slowness"] = {"time": pygame.time.get_ticks(), "duration": duration}

                if "knockback effect on enemies 2x" in current_sword.major_affixes:
                    enemy.knockback_velocity *= 2

                # Normal sword effects
                if "freezes enemy" in current_sword.major_affixes:
                    enemy.status_effects["freeze"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": 1000 * (1.1 ** get_attribute_level())
                    }
                    
                if "slows enemy" in current_sword.major_affixes:
                    enemy.status_effects["slowness"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": 2000 * (1.1 ** get_attribute_level())
                    }

                if "burns enemy" in current_sword.major_affixes:
                    enemy.status_effects["burn"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": 3000 * (1.1 ** get_attribute_level()),
                        "tick": 300,
                        "next_tick": pygame.time.get_ticks() + 300,
                    }

                if "poisons enemy" in current_sword.major_affixes:
                    enemy.status_effects["poison"] = {
                        "time": pygame.time.get_ticks(),
                        "duration": 6000 * (1.1 ** get_attribute_level()),
                        "tick": 1000,
                        "next_tick": pygame.time.get_ticks() + 2000,
                    }

def draw_boss_health_bars():
    boss_enemies = [enemy for enemy in enemies if enemy.type == "conjivictus"]
    bar_y = 40
    for boss in boss_enemies:
        bar_x = WIDTH // 2 - 250
        bar_width = 500
        bar_height = 30
        ratio = max(0, boss.hp / 500)
        fill_width = int(bar_width * ratio)

        pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (180, 0, 180), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 4)
        
        bar_y += 50  # next boss if multiple



def draw_stones():
    for stone in stones:
        draw_x = stone[0] - camera_x + WIDTH // 2 + int(world_offset_x)
        draw_y = stone[1] - camera_y + HEIGHT // 2 + int(world_offset_y)
        grass_scaled = pygame.transform.scale(grass_image, (stone[2] * 2, stone[2] * 2))
        screen.blit(grass_scaled, (draw_x - stone[2], draw_y - stone[2]))


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



# Draw boss HP bars
bosses = [e for e in enemies if e.type == "conjivictus"]
for i, boss in enumerate(bosses):
    bar_width = 400
    bar_height = 20
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 40 + i * 30  # 40px from top, 30px per bar stacked
    ratio = boss.hp / 500
    pygame.draw.rect(screen, (100, 0, 100), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (255, 0, 255), (bar_x, bar_y, bar_width * ratio, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3)


def draw_stats():
    font = pygame.font.SysFont(None, 36)
    crit_percent = round(get_crit_chance() * 100, 2)
    if "Double crit chance" in current_sword.minor_affixes:
        crit_percent *= 2


    lines = [
        ("Sword Type: " + current_sword.sword_type, sword_colors[current_sword.sword_type]),
        ("Base Damage: " + str(current_sword.base_damage), (255, 255, 255)),
        ("Total Damage: " + str(round(calculate_sword_damage(), 2)), (255, 255, 255)),
        ("Crit Chance: " + str(crit_percent) + "%", (255, 100, 100)),
        ("BRUTALITY (1): " + str(player_brutality), sword_colors["BRUTALITY"]),
        ("TACTICS (2): " + str(player_tactics), sword_colors["TACTICS"]),
        ("SURVIVAL (3): " + str(player_survival), sword_colors["SURVIVAL"]),
    ]
    for i, (text, color) in enumerate(lines):
        rendered = font.render(text, True, color)
        screen.blit(rendered, (WIDTH - 350, 30 + i * 40))
    





def handle_events(events):
    global sword_thrust, thrust_velocity, thrust_distance, running
    global is_dashing, last_dash_time, dash_direction
    global player_brutality, player_tactics, player_survival
    global current_sword, inventory_open  # inventory_open je tukaj pozabil!
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and selecting_scroll_attribute:
            handle_scroll_selection_click(pygame.mouse.get_pos())


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not sword_thrust:
            sword_thrust = True
            thrust_velocity = 10
            thrust_distance = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if any([pygame.key.get_pressed()[pygame.K_w], pygame.key.get_pressed()[pygame.K_s],
                        pygame.key.get_pressed()[pygame.K_a], pygame.key.get_pressed()[pygame.K_d]]):
                    current_time = pygame.time.get_ticks()
                    if current_time - last_dash_time >= dash_cooldown:
                        is_dashing = True
                        last_dash_time = current_time
            if event.key == pygame.K_g:
                generate_new_sword(current_sword)

            if event.key == pygame.K_3 and player_ability_1:
                player_ability_1.try_activate()
            if event.key == pygame.K_4 and player_ability_2:
                player_ability_2.try_activate()


            if event.key == pygame.K_1:
                if sword_1 is not None:
                    current_sword = sword_1
                elif sword_2 is not None:
                    current_sword = sword_2

            if event.key == pygame.K_2:
                if sword_2 is not None:
                    current_sword = sword_2
                elif sword_1 is not None:
                    current_sword = sword_1

            if event.key == pygame.K_e and not selecting_sword:
                inventory_open = not inventory_open
            if event.key == pygame.K_TAB and not selecting_sword:
                inventory_open = not inventory_open



def dash():
    global player_x, player_y, is_dashing, dash_direction
    if is_dashing:
        dash_distance = dash_speed * 7
        new_x = player_x + dash_direction[0] * dash_distance
        new_y = player_y + dash_direction[1] * dash_distance

        WALL_MIN = -2100
        WALL_MAX = 2100
        PLAY_MIN = -2000
        PLAY_MAX = 2000

        # Check if after dash, player would land inside playable area
        if PLAY_MIN <= new_x <= PLAY_MAX and PLAY_MIN <= new_y <= PLAY_MAX:
            player_x = new_x
            player_y = new_y
        else:
            # Player dashed into wall! Throw them back into arena.
            if new_x < PLAY_MIN:
                player_x = PLAY_MIN + 20
            elif new_x > PLAY_MAX:
                player_x = PLAY_MAX - 20
            else:
                player_x = new_x

            if new_y < PLAY_MIN:
                player_y = PLAY_MIN + 20
            elif new_y > PLAY_MAX:
                player_y = PLAY_MAX - 20
            else:
                player_y = new_y

        is_dashing = False


def is_critical_hit():
    if "Increases your movement speed for 5 seconds after a critical hit" in current_sword.major_affixes:
        global speed_boost_active, speed_boost_timer
        speed_boost_active = True
        speed_boost_timer = pygame.time.get_ticks()

    return random.random() < get_crit_chance()


def get_crit_chance():
    base_chance = 0.01
    if current_sword.sword_type == "BRUTALITY":
        multiplier = 1.2 ** player_brutality
    elif current_sword.sword_type == "TACTICS":
        multiplier = 1.3 ** player_tactics
    elif current_sword.sword_type == "SURVIVAL":
        multiplier = 1.1 ** player_survival
    else:
        multiplier = 1.0

    if "double_crit" in current_sword.effects:
        multiplier *= 2

    return base_chance * multiplier

# Main loop
running = True
max_health= get_scaled_stats()
player_health = max_health
spawn_sword_timer = 0
spawn_sword_interval = 5000

while running:
    # 1. PRIDOBIMO DOGODKE samo enkrat
    events = pygame.event.get()

    # 2. Posredujemo dogodke vsem handlerjem
    handle_sword_pickup_events(events)
    handle_events(events)

    if selecting_scroll_attribute:
        # Dim screen
        # Draw the scroll selection UI
        draw_scroll_selection()

        # Pause everything else
        pygame.display.update()
        clock.tick(60)
        continue



    # 3. Če je meni (UI) odprt, ne izvajaj igre naprej
    if inventory_open or selecting_sword or selecting_ability:

        screen.fill((26, 36, 33))
        draw_stones()

        for pickup in sword_pickups:
            pickup.draw()

        for p in particles:
            p.update()
            p.draw()

        for dmg in damage_numbers:
            dmg.update()
            dmg.draw()
        
        if chest_ui_weapons:
            # Skip drawing inventory swords when chest is open
            sword_box1 = sword_box2 = sword_box3 = None


        draw_sword_selection_ui()
        pygame.display.flip()
        clock.tick(60)
        continue  # preskoči glavno logiko igre

    # 4. Glavni del igre
    screen.fill((26, 36, 33))
    keys = pygame.key.get_pressed()
    handle_movement(keys)

    # ... (vse ostalo ostane, npr. posodabljanje stanja, prikaz sovražnikov itd.)





#    current_time = pygame.time.get_ticks()
#    if current_time - spawn_sword_timer > spawn_sword_interval:
#        spawn_sword_pickup()
#        spawn_sword_timer = current_time

  


    max_health= get_scaled_stats()



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

    now = pygame.time.get_ticks()

    dash()

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= enemy_spawn_time:
        if not boss_spawned:
            if score < 100:
                enemy_type = "normal"
            elif score < 200:
                enemy_type = random.choices(["normal", "rocketeer"], weights=[80, 20])[0]
            elif score < 400:
                enemy_type = random.choices(["normal", "rocketeer", "harpooner"], weights=[60, 25, 15])[0]
            elif score < 700:
                enemy_type = random.choices(["normal", "rocketeer", "harpooner", "teleporter"], weights=[40, 25, 20, 15])[0]
            else:
                # After 350, no enemies spawn until boss is killed
                enemy_type = None

            if enemy_type:
                enemies.append(Enemy(enemy_type))

        last_spawn_time = current_time

        if speed_boost_active:
            if pygame.time.get_ticks() - speed_boost_timer > speed_boost_duration:
                speed_boost_active = False
            else:
                player_speed = 7  # temporarily increased
        else:
            player_speed = 5


    for enemy in enemies:
        enemy.move_towards_player(player_x, player_y)
        enemy.draw()
        dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
        if dist < enemy.size + 35:
            last_hit = enemy_hit_timers.get(enemy.id, 0)
            if current_time - last_hit > invincibility_duration:
                # Base damage
                damage_taken = enemy.damage

                # Affix: +100% damage inflicted on enemies, +100% damage taken!
                if "+100% damage inflicted on enemies, +100% damage taken!" in current_sword.major_affixes:
                    damage_taken *= 2

                # Affix: +300% damage inflicted on enemies, +300% damage taken!
                if "+300% damage inflicted on enemies, +300% damage taken!" in current_sword.major_affixes:
                    damage_taken *= 4

                player_health -= damage_taken
                camera_shake_intensity = 15  # set initial shake strength

                damage_flash_time = pygame.time.get_ticks()

                enemy_hit_timers[enemy.id] = current_time

                dx, dy = player_x - enemy.x, player_y - enemy.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist != 0:
                    player_knockback_direction = (dx / dist, dy / dist)
                    player_knockback = 1
                    player_knockback_velocity = 15

    
    for chest in chests:
        chest.update()

        chest.draw()
        if chest.is_near_player() and not chest.opened:
            font = pygame.font.SysFont(None, 28)
            text = font.render("Press [F] to open chest", True, (255, 255, 255))
            draw_x = chest.x - camera_x + WIDTH // 2
            draw_y = chest.y - camera_y + HEIGHT // 2
            screen.blit(text, (draw_x - 30, draw_y - 80))


            keys = pygame.key.get_pressed()
            if keys[pygame.K_f]:
                chest.open()
                selecting_sword = True
                new_sword_candidate = None
                if isinstance(chest, SwordChest):
                    chest_ui_weapons = chest.weapons
                elif isinstance(chest, AbilityChest):
                    chest_ui_weapons = chest.abilities
                    selecting_ability = True

                chest_being_opened = chest





    new_enemies = []
    for enemy in enemies:
        if not enemy.is_alive():
            # Speed boost on kill
            if "Increases your movement speed for 5 seconds after killing an enemy" in current_sword.major_affixes:
                speed_boost_active = True
                speed_boost_timer = pygame.time.get_ticks()

            # === 💥 LEGENDARY EXPLOSIONS ===
            explosion_radius = 250
            now = pygame.time.get_ticks()

            def apply_aoe_effect(effect_name, color, duration, tick=None, tick_interval=None):
                for other_enemy in enemies:
                    if other_enemy.is_alive() and other_enemy != enemy:
                        dist = math.hypot(other_enemy.x - enemy.x, other_enemy.y - enemy.y)
                        if dist <= explosion_radius:
                            other_enemy.status_effects[effect_name] = {
                                "time": now,
                                "duration": duration,
                                **({"tick": tick, "next_tick": now + tick} if tick else {})
                            }

                # Particles explosion
                for _ in range(40):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 6)
                    px = enemy.x + math.cos(angle) * 20
                    py = enemy.y + math.sin(angle) * 20
                    p = Particle(px, py, color, behavior=effect_name)
                    p.vx = math.cos(angle) * speed
                    p.vy = math.sin(angle) * speed
                    particles.append(p)

            # Poison cloud
            if "enemies explode in poison cloud on death" in current_sword.legendary_affixes:
                apply_aoe_effect("poison", (0, 255, 0), 6000, tick=1000, tick_interval=1000)

            # Burn cloud
            if "enemies explode in burn cloud on death" in current_sword.legendary_affixes:
                apply_aoe_effect("burn", (255, 100, 0), 3000, tick=300, tick_interval=300)

            # Freeze cloud
            if "enemies explode in freeze cloud on death" in current_sword.legendary_affixes:
                apply_aoe_effect("freeze", (0, 100, 255), 1000)

            # Slow cloud
            if "enemies explode in slow cloud on death" in current_sword.legendary_affixes:
                apply_aoe_effect("slowness", (128, 128, 128), 2000)

            # Splošni eksplozijski particles
            for _ in range(20):
                particles.append(Particle(enemy.x, enemy.y, enemy.color))

        if enemy.is_alive():
            new_enemies.append(enemy)
        if enemy.type == "harpooner" and enemy.just_hit_player:
            player_health -= enemy.damage
            camera_shake_intensity = 15  # set initial shake strength

            damage_flash_time = pygame.time.get_ticks()

            enemy.just_hit_player = False  # Reset after damage
    enemies = new_enemies

    if score >= 700 and not boss_spawned:
        enemies.append(Enemy("conjivictus"))
        boss_spawned = True


    # Apply camera shake
    if camera_shake_intensity > 0.5:
        camera_x += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
        camera_y += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
        camera_shake_intensity *= camera_shake_decay
    else:
        camera_shake_intensity = 0


    follow_speed = 0.08
    camera_x += (player_x - camera_x) * follow_speed
    camera_y += (player_y - camera_y) * follow_speed

    player_draw_x = WIDTH // 2
    player_draw_y = HEIGHT // 2

    draw_stones()
    draw_walls()

    # And then call it after drawing enemies
    draw_boss_health_bars()

    for p in particles:
        p.update()
        p.draw()
    particles = [p for p in particles if p.is_alive()]

    for dmg in damage_numbers:
        dmg.update()
        dmg.draw()
    damage_numbers = [d for d in damage_numbers if d.is_alive()]

    for pickup in sword_pickups:
        pickup.draw()

    for knife in knives:
        knife.update()
        knife.draw()
    knives = [k for k in knives if k.is_alive()]

    # Update and draw bombs
    for bomb in bombs:
        bomb.update()
        bomb.draw()
    bombs = [b for b in bombs if b.is_alive()]
    draw_score()

    for rocket in rockets:
        rocket.update()
        rocket.draw()


    # Spawn scrolls over time
    spawn_scroll_timer += clock.get_time()
    if spawn_scroll_timer >= spawn_scroll_interval:
        spawn_scroll()
        spawn_chest()
        spawn_scroll_timer = 0

    # Healing over time
    healing_rate = 0.05  # amount healed per second
    delta_time = clock.get_time() / 1000  # time since last frame in seconds
    if player_health < max_health:
        player_health += healing_rate * delta_time * max_health
        if player_health > max_health:
            player_health = max_health




    for scroll in scroll_pickups:
        scroll.draw()
        draw_scroll_selection()
        if scroll.is_near_player():
            font = pygame.font.SysFont(None, 36)
            text = font.render("Press F to read scroll", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 200))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_f]:
                open_scroll(scroll)
                break


    for ability in ability_pickups:
        ability.draw()



    # Če izbiramo meč za zamenjavo, nariši UI
    if selecting_sword:
        draw_sword_selection_ui()
        pygame.display.flip()
        continue

    update_sword(player_draw_x, player_draw_y)
    draw_player(player_draw_x, player_draw_y)
#    draw_stats()
    draw_custom_ui()
    draw_equipped_slots()

    # Screen flash if recently damaged
    if pygame.time.get_ticks() - damage_flash_time < damage_flash_duration:
        red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        red_overlay.fill((255, 0, 0, 100))  # semi-transparent red
        screen.blit(red_overlay, (0, 0))


    pygame.display.flip()
    clock.tick(60)


affix_conn.close()
pygame.quit()
