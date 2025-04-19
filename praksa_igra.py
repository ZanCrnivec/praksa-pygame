import pygame
import random
import math
from enum import Enum

pygame.init()




WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

sword_images = {
    "BRUTALITY": pygame.image.load("brutality_sword.png").convert_alpha(),
    "TACTICS": pygame.image.load("tactics_sword.png").convert_alpha(),
    "SURVIVAL": pygame.image.load("survival_sword.png").convert_alpha()
}

player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5
dash_speed = 50
dash_cooldown = 500
last_dash_time = 0
is_dashing = False
dash_direction = (0, 0)
chest_ui_weapons = []
chest_being_opened = None
player_ability_1 = None
player_ability_2 = None



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
    BURN = "burn"
    BOMB_SMALL = "bomb_small"
    BOMB_BIG = "bomb_big"
    BOMB_SCATTER = "bomb_scatter"
    THROWING_KNIFE = "throwing_knife"
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

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < enemy.size:
                damage = calculate_sword_damage() * 1.5
                enemy.take_damage(damage, player_x, player_y)
                enemy.trigger_flash((255, 255, 255))
                damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage))
                self.life = 0  # disappear on hit
                break

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x - camera_x + WIDTH // 2), int(self.y - camera_y + HEIGHT // 2)), 8)

    def is_alive(self):
        return self.life > 0

# global list of knives
knives = []

def spawn_knife(self):
    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
    knives.append(ThrowingKnife(player_x, player_y, angle))



class Ability:
    roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]

    minor_pool = [
        "reduced cooldown",
        "+20% area of effect",
        "+15% damage",
        "cooldown resets on kill"
    ]

    major_pool = [
        "double explosion",
        "+40% damage",
        "freezes enemies in larger radius",
        "knockback x2",
        "cooldown halved when under 50% HP"
    ]

    legendary_pool = [
        "+300% damage on ability use",
        "heals 10% on ability hit",
        "burn/freeze spreads to nearby enemies",
        "ability triggers twice"
    ]
    @property
    def is_legendary(self):
        return len(self.legendary_affixes) > 0


    def __init__(self, ability_type, sword_type="TACTICS"):
        self.ability_type = ability_type
        self.sword_type = sword_type
        self.gear_level = random.randint(1, 7)
        self.minor_affixes = random.sample(self.minor_pool, k=random.randint(0, min(2, self.gear_level)))
        self.major_affixes = random.sample(self.major_pool, k=random.randint(0, min(2, self.gear_level // 2)))
        self.legendary_affixes = random.sample(self.legendary_pool, k=random.randint(0, 1)) if random.random() < 0.1 else []
        self.cooldown = self.calculate_base_cooldown()
        self.last_used = 0

    def calculate_base_cooldown(self):
        base = {
            AbilityType.FREEZE: 5000,
            AbilityType.BURN: 5000,
            AbilityType.BOMB_SMALL: 3000,
            AbilityType.BOMB_BIG: 7000,
            AbilityType.BOMB_SCATTER: 6000,
            AbilityType.THROWING_KNIFE: 2000
        }.get(self.ability_type, 5000)

        if "reduced cooldown" in self.minor_affixes:
            base *= 0.8
        if "cooldown halved when under 50% HP" in self.major_affixes:
            base *= 0.5  # Should be dynamic based on HP
        return int(base)

    def is_ready(self, now):
        return now - self.last_used >= self.cooldown

    def activate(self, now):
        self.last_used = now
        # Placeholder: return description of action
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
        elif self.ability_type == AbilityType.BOMB_SMALL:
            self.spawn_bomb(radius=60, damage=calculate_sword_damage() * 1.5)
        elif self.ability_type == AbilityType.BOMB_BIG:
            self.spawn_bomb(radius=120, damage=calculate_sword_damage() * 3)
        elif self.ability_type == AbilityType.BOMB_SCATTER:
            for _ in range(5):
                self.spawn_bomb(radius=50, damage=calculate_sword_damage())
        elif self.ability_type == AbilityType.THROWING_KNIFE:
            self.spawn_knife()

    def activate_freeze(self):
        for enemy in enemies:
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
            if dist < 300:
                enemy.status_effects["freeze"] = {
                    "time": pygame.time.get_ticks(),
                    "duration": 2000 * (1.1 ** get_attribute_level())
                }

    def activate_burn(self):
        for enemy in enemies:
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
            if dist < 300:
                enemy.status_effects["burn"] = {
                    "time": pygame.time.get_ticks(),
                    "duration": 3000 * (1.1 ** get_attribute_level()),
                    "tick": 300,
                    "next_tick": pygame.time.get_ticks() + 300
                }

    def spawn_bomb(self, radius, damage):
        for enemy in enemies:
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
            if dist <= radius:
                enemy.take_damage(damage, player_x, player_y)
                enemy.trigger_flash((255, 100, 0))
                damage_numbers.append(DamageNumber(enemy.x, enemy.y, damage))
                for _ in range(10):
                    particles.append(Particle(enemy.x, enemy.y, (255, 50, 0), behavior="burn"))

    def spawn_knife(self):
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        vx = math.cos(angle) * 12
        vy = math.sin(angle) * 12
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - HEIGHT // 2, mx - WIDTH // 2)
        knives.append(ThrowingKnife(player_x, player_y, angle))



class Chest:
    def __init__(self, x, y, rarity):
        self.x = x
        self.y = y
        self.rarity = rarity
        self.image = pygame.transform.scale(chest_images[rarity], (210, 110))
        self.opened = False
        self.weapons = []

    def draw(self):
        if not self.opened:
            draw_x = self.x - camera_x + WIDTH // 2
            draw_y = self.y - camera_y + HEIGHT // 2
            screen.blit(self.image, (draw_x - 32, draw_y - 32))

    def is_near_player(self):
        return math.hypot(player_x - self.x, player_y - self.y) < 80

    def open(self):
        if self.opened:
            return
        self.opened = True
        self.weapons = []
        rarity_data = chest_rarities[self.rarity]

        for _ in range(3):
            sword = Sword()
            sword.gear_level = random.randint(*rarity_data["gear_range"])
            sword.base_damage = random.randint(3, 7) + sword.gear_level
            sword.sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])
#            sword.effects = random.sample(possible_effects, k=random.randint(0, 2))

            if rarity_data["legendary"] > 0 and random.random() < rarity_data["legendary"]:
                sword.is_legendary = True
                sword.legendary_affixes = random.sample(Sword.legendary_pool, k=1)
                sword.major_affixes = random.sample(Sword.major_pool, k=rarity_data["major"])
                
                # ✅ Dodaj minor affixe
                num_minor = random.randint(0, sword.gear_level)
                sword.minor_affixes = random.sample(Sword.minor_pool, k=min(num_minor, len(Sword.minor_pool)))
            else:
                num_minor = random.randint(0, sword.gear_level)
                sword.minor_affixes = random.sample(Sword.minor_pool, k=min(num_minor, len(Sword.minor_pool)))
                sword.major_affixes = random.sample(Sword.major_pool, k=rarity_data["major"])


            self.weapons.append(sword)


chests = []

def spawn_chest():
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    rarity = random.choices(["common", "rare", "epic", "legendary"], weights=[25, 25, 25, 25])[0]
    chests.append(Chest(x, y, rarity))



speed_boost_active = False
speed_boost_timer = 0
speed_boost_duration = 5000  # in ms
speed_boost_amount = 2


camera_x, camera_y = player_x, player_y

sword_thrust = False
thrust_velocity = 0
thrust_distance = 0
sword_hit_enemies = set()


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

    selected_text = font.render("Selected: Sword 1" if current_sword == sword_1 else "Selected: Sword 2", True, (255, 255, 255))
    screen.blit(selected_text, (WIDTH - 350, 320))

def draw_equipped_slots():
    slot_size = 70
    spacing = 12
    section_gap = 40  # gap between weapon and ability slots
    start_x = 30
    start_y = HEIGHT - 140
    font = pygame.font.SysFont(None, 24)
    number_font = pygame.font.SysFont(None, 22)

    slots = [sword_1, sword_2, player_ability_1, player_ability_2]

    for i, item in enumerate(slots):
        x = start_x + i * (slot_size + spacing) + (section_gap if i >= 2 else 0)
        y = start_y

        rect = pygame.Rect(x, y, slot_size, slot_size)

        # Draw number label above slot
        number_text = number_font.render(str(i + 1), True, (255, 255, 255))
        num_rect = number_text.get_rect(center=(x + slot_size // 2, y - 12))
        screen.blit(number_text, num_rect)

        # Determine attribute type
        attr_color = (60, 60, 60)  # default for empty slots
        is_legendary = False

        if item:
            sword_type = getattr(item, "sword_type", None)
            if sword_type in sword_colors:
                base = sword_colors[sword_type]
                attr_color = tuple(int(c * 0.4) for c in base)
            is_legendary = getattr(item, "is_legendary", False)

        # Background
        pygame.draw.rect(screen, attr_color, rect)

        # Border
        border_color = (255, 215, 0) if is_legendary else (255, 255, 255)
        pygame.draw.rect(screen, border_color, rect, 3)

        # Inner color (thin square)
        if item:
            inner_color = sword_colors.get(getattr(item, "sword_type", ""), (0, 0, 0))
            inner_rect = rect.inflate(-80, -80)
            pygame.draw.rect(screen, inner_color, inner_rect)

        # Weapon icons (rotated)
        if i < 2 and item:
            icon = sword_images.get(item.sword_type)
            if icon:
                icon_scaled = pygame.transform.scale(icon, (60, 30))  # elongate
                icon_rotated = pygame.transform.rotate(icon_scaled, 45)
                icon_rect = icon_rotated.get_rect(center=rect.center)
                screen.blit(icon_rotated, icon_rect)

        # Highlight selected sword
        if (i == 0 and current_sword == sword_1) or (i == 1 and current_sword == sword_2):
            pygame.draw.rect(screen, (255, 255, 255), rect, 5)

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








def generate_new_sword(sword):
    sword.generate_random()



def calculate_sword_damage():
    return current_sword.get_damage(player_brutality, player_tactics, player_survival)


def get_attribute_level():
    return current_sword.get_attribute_level(player_brutality, player_tactics, player_survival)





def get_scaled_stats():
    hp = 100 * ((1.1 ** player_brutality) * (1.1 ** player_tactics) * (1.5 ** player_survival))
    stamina = 100 * ((1.2 ** player_brutality) * (1.5 ** player_tactics) * (1.2 ** player_survival))
    return hp, stamina


class Sword:
    roman_levels = ["I", "II", "III", "IV", "V", "VI", "VII"]

    minor_pool = [
        "+40% damage on burning target",
        "+40% damage on poisoned target",
        "+40% damage on frozen target",
        "+40% damage on slowed target",
        "Critical hits +20% damage",
        "+50% damage when you are at max HP",
        "+20% damage",
        "Critical hits +30% damage"
        "Double crit chance"
    ]

    major_pool = [
        "colorless", "+15% damage", "+40% damage",
        "+100% damage inflicted on enemies, +100% damage taken!",
        "+300% damage inflicted on enemies, +300% damage taken!",
        "1% of HP recovered per attack",
        "poisons enemy", "burns enemy", "freezes enemy", "slows enemy",
        "Increases your movement speed for 5 seconds after a critical hit",
        "Increases your movement speed for 5 seconds after killing an enemy",
        "knockback effect on enemies 2x"
    ]

    legendary_pool = [
        "Critical hits +50% damage",
        "heals 3% on hit",
        "being hit by an enemy does 10% of damage on enemy",
        "+10% chance of critical hit",
        "+15% chance of critical hit",
        "+300% damage inflicted on enemies!",
        "enemies explode in poison cloud on death",
        "enemies explode in burn cloud on death",
        "enemies explode in freeze cloud on death",
        "enemies explode in slow cloud on death",
        "speed boost 10s after kill",
        "speed boost 10s after crit"
    ]

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
        self.base_damage = random.randint(3, 7) + self.gear_level
        self.sword_type = random.choice(["BRUTALITY", "TACTICS", "SURVIVAL"])

        if self.is_legendary:
            # Determine sword type based on highest player attribute
            max_attr = max(player_brutality, player_tactics, player_survival)
            if player_brutality == max_attr:
                self.sword_type = "BRUTALITY"
            elif player_tactics == max_attr:
                self.sword_type = "TACTICS"
            elif player_survival == max_attr:
                self.sword_type = "SURVIVAL"

            self.major_affixes = random.sample(self.major_pool, k=random.randint(1, 3))
            self.legendary_affixes = random.sample(self.legendary_pool, k=random.randint(1, 2))
        else:
            self.minor_affixes = random.sample(self.minor_pool, k=random.randint(1, self.gear_level))
            if random.random() < 0.3:
                self.major_affixes = [random.choice(self.major_pool)]


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




sword_1 = Sword()
sword_2 = Sword()
current_sword = sword_1

# Auto-equip throwing knife in ability slot 1
player_ability_1 = Ability(AbilityType.THROWING_KNIFE)



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

        # Flash effect
        self.flash_color = None
        self.flash_time = 0
        self.flash_duration = 100  # milliseconds

    def trigger_flash(self, color):
        self.flash_color = color
        self.flash_time = pygame.time.get_ticks()

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        now = pygame.time.get_ticks()

        # Freeze effect
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

        if "slowness" in self.status_effects:
            s = self.status_effects["slowness"]
            if now - s["time"] < s["duration"]:
                if "last_particle" not in s or now - s["last_particle"] > 200:
                    offset_x = random.uniform(-self.size * 0.8, self.size * 0.8)
                    offset_y = random.uniform(-self.size * 0.8, self.size * 0.8)
                    particles.append(Particle(self.x + offset_x, self.y + offset_y, (128, 128, 128), behavior="slowness"))
                    s["last_particle"] = now

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

        # Burn effect
        if "burn" in self.status_effects:
            b = self.status_effects["burn"]
            if now - b["time"] < b["duration"]:
                if now >= b["next_tick"]:
                    burn_damage = calculate_sword_damage() * 0.1
                    self.hp -= burn_damage
                    self.trigger_flash((255, 120, 0))  # orange-ish

                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, burn_damage))
                    self.trigger_flash((255, 120, 0))  # orange
                    b["next_tick"] = now + b["tick"]
                    for _ in range(random.randint(6, 15)):
                        particles.append(Particle(self.x, self.y, (255, 100, 0), behavior="burn"))
            else:
                del self.status_effects["burn"]

        # Poison effect
        if "poison" in self.status_effects:
            p = self.status_effects["poison"]
            if now - p["time"] < p["duration"]:
                if now >= p["next_tick"]:
                    poison_damage = calculate_sword_damage() * 0.3
                    self.hp -= poison_damage
                    self.trigger_flash((0, 255, 0))  # green

                    damage_numbers.append(DamageNumber(self.x, self.y - self.size, poison_damage))
                    self.trigger_flash((0, 255, 0))  # green
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
            multiplier = 1.5 if "knockback effect on enemies 2x" in current_sword.major_affixes else 1.0
            self.knockback_velocity = 10 * multiplier
            self.knockback_velocity = min(self.knockback_velocity, 12)


    def draw(self):
        draw_color = self.color
        now = pygame.time.get_ticks()

        if self.flash_color and now - self.flash_time < self.flash_duration:
            draw_color = self.flash_color
        else:
            self.flash_color = None

        pygame.draw.circle(
            screen,
            draw_color,
            (int(self.x - camera_x + WIDTH // 2), int(self.y - camera_y + HEIGHT // 2)),
            self.size
        )

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
            self.vx += random.uniform(-0.3, 0.3)
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

MINOR_LINE_HEIGHT = 22
MAJOR_LINE_HEIGHT = 22
LEGENDARY_LINE_HEIGHT = 22
        
# --- NOVI DELI KODE ZA MEČE NA MAPI ---
class SwordPickup:
    def __init__(self, x, y, sword):
        self.x = x
        self.y = y
        self.sword = sword
        self.size = 48  # velikost kvadrata

    def draw(self):
        color = sword_colors[self.sword.sword_type]
        draw_x = int(self.x - camera_x + WIDTH // 2)
        draw_y = int(self.y - camera_y + HEIGHT // 2)
        img = sword_images[self.sword.sword_type]
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
            gear_text = f"{self.sword.sword_type.capitalize()} Sword {Sword.roman_levels[self.sword.gear_level - 1]}"
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
    sword.generate_random()
    sword_pickups.append(SwordPickup(x, y, sword))

# Flag za prikaz UI za zamenjavo
selecting_sword = False
new_sword_candidate = None

inventory_open = False

def draw_sword_selection_ui():
    global sword_box1, sword_box2, sword_box3

    sword_box1 = sword_box2 = sword_box3 = None

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont(None, 48)
    if chest_ui_weapons:
        if chest_ui_weapons and chest_being_opened:
            rarity = chest_being_opened.rarity.capitalize()
            color_map = {
                "Common": (200, 200, 200),
                "Rare": (0, 200, 255),
                "Epic": (160, 32, 240),
                "Legendary": (255, 215, 0)
            }
            color = color_map.get(rarity, (255, 255, 255))
            title_text = f"{rarity} Chest"
            screen.blit(font.render(title_text, True, color), (WIDTH // 2 - 100, 40))

        screen.blit(font.render("CHOOSE A SWORD", True, (255, 255, 255)), (WIDTH // 2 - 150, HEIGHT - 60))

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





    def draw_sword_box(x, y, sword, title):
        rect = pygame.Rect(x, y, 360, 600)
        base_border_color = (255, 215, 0) if sword.is_legendary else sword_colors[sword.sword_type]
        hover = rect.collidepoint(pygame.mouse.get_pos()) and selecting_sword and title != "New Sword"
        border_color = (255, 255, 255) if hover else base_border_color

        # Gradient ozadje
        gradient_surface = pygame.Surface((rect.width, rect.height))
        base_color = pygame.Color(
            int(border_color[0] * 0.3),
            int(border_color[1] * 0.3),
            int(border_color[2] * 0.3)
        )
        for i in range(rect.height):
            color = base_color.lerp((15, 15, 15), i / rect.height * 0.6)
            pygame.draw.line(gradient_surface, color, (0, i), (rect.width, i))
        screen.blit(gradient_surface, (x, y))

        # Rob
        pygame.draw.rect(screen, border_color, rect, 4)

        # Rotiran meč
        img = sword_images[sword.sword_type]
        img = pygame.transform.scale(img, (80, 40))
        img = pygame.transform.rotate(img, 45)
        img_rect = img.get_rect(topright=(x + rect.width - 10, y + 10))
        screen.blit(img, img_rect)

        font = pygame.font.SysFont(None, 24)
        bold_font = pygame.font.SysFont(None, 24, bold=True)
        big_font = pygame.font.SysFont(None, 28)
        legendary_font = pygame.font.SysFont(None, 28, bold=True)

        # Naslov z gear levelom
        gear_text = f"{sword.sword_type.capitalize()} Sword {Sword.roman_levels[sword.gear_level - 1]}"
        if sword.is_legendary:
            gear_text += " L"

        if sword.major_affixes:
            gear_text += " *"
        if sword.is_legendary:
            gear_text = gear_text.upper()
            title_color = (255, 215, 0)  # gold

        else:
            title_color = border_color

        screen.blit(bold_font.render(title, True, title_color), (x + 15, y + 12))
        screen.blit(big_font.render(gear_text, True, title_color), (x + 15, y + 38))

        # Damage
        total_dmg = round(sword.get_damage(player_brutality, player_tactics, player_survival), 2)
        screen.blit(font.render("Total Damage:", True, (230, 230, 230)), (x + 15, y + 64))
        screen.blit(font.render(str(total_dmg), True, title_color), (x + 150, y + 64))

        y_offset = y + 100
        screen.blit(font.render("Effects:", True, (255, 255, 255)), (x + 15, y_offset))
        y_offset += 25

        # Običajni učinki
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

                # MINOR affixi (zeleni, manjši font)
        # MINOR affixi (zeleni, manjši font)
        minor_font = pygame.font.SysFont(None, 22)
        for affix in sword.minor_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", minor_font, (0, 255, 100), x + 25, y_offset, 310, 20)




        # MAJOR affixi (beli)
        for affix in sword.major_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", font, (255, 255, 255), x + 25, y_offset, 310, 22)



        # LEGENDARY affixi (rumeni, večji)
        for affix in sword.legendary_affixes:
            y_offset = draw_wrapped_text(screen, f"- {affix}", legendary_font, (255, 255, 0), x + 25, y_offset, 310, 24)





                


        return rect

    # === INVENTORY OPEN ===
    if inventory_open and not chest_ui_weapons and not selecting_sword:
        sword_box1 = draw_sword_box(WIDTH // 2 - 550, 200, sword_1, "Sword 1")
        sword_box2 = draw_sword_box(WIDTH // 2 - 180, 200, sword_2, "Sword 2")

    # === SWORD PICKUP UI (from ground) ===
    elif selecting_sword and new_sword_candidate and not chest_ui_weapons:
        title_text = "Choose a Sword to Replace"
        font = pygame.font.SysFont(None, 48)
        screen.blit(font.render(title_text, True, (255, 255, 255)), (WIDTH // 2 - 200, 40))

        sword_box3 = draw_sword_box(WIDTH // 2 + 480, 200, new_sword_candidate, "New Sword")
        sword_box1 = draw_sword_box(WIDTH // 2 - 480, 200, sword_1, "Sword 1")
        sword_box2 = draw_sword_box(WIDTH // 2, 200, sword_2, "Sword 2")

    # === CHEST OPEN UI ===
    elif chest_ui_weapons:
        if chest_being_opened:
            rarity = chest_being_opened.rarity.capitalize()
            color_map = {
                "Common": (200, 200, 200),
                "Rare": (0, 200, 255),
                "Epic": (160, 32, 240),
                "Legendary": (255, 215, 0)
            }
            color = color_map.get(rarity, (255, 255, 255))
            title_text = f"{rarity} Chest"
            font = pygame.font.SysFont(None, 48)
            screen.blit(font.render(title_text, True, color), (WIDTH // 2 - 100, 40))

        if len(chest_ui_weapons) >= 3:
            sword_box1 = draw_sword_box(WIDTH // 2 - 545, 200, chest_ui_weapons[0], "Sword A")
            sword_box2 = draw_sword_box(WIDTH // 2 - 145, 200, chest_ui_weapons[1], "Sword B")
            sword_box3 = draw_sword_box(WIDTH // 2 + 245, 200, chest_ui_weapons[2], "Sword C")

        font = pygame.font.SysFont(None, 48)
        screen.blit(font.render("CHOOSE A SWORD", True, (255, 255, 255)), (WIDTH // 2 - 150, HEIGHT - 60))

    # === DRAW ARROW FROM NEW SWORD (box3) TO HOVERED SWORD (box1/2) ===
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
    global selecting_sword, new_sword_candidate, sword_pickups
    global sword_1, sword_2, inventory_open
    global chest_ui_weapons, chest_being_opened

    keys = pygame.key.get_pressed()
    for event in events:

        # F - pick up sword from ground
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and not selecting_sword and not inventory_open:
                for pickup in sword_pickups:
                    if pickup.is_near_player():
                        selecting_sword = True
                        new_sword_candidate = pickup.sword
                        sword_pickups.remove(pickup)
                        break

            elif event.key == pygame.K_g:
                # Cancel sword selection
                if selecting_sword and new_sword_candidate:
                    sword_pickups.append(SwordPickup(player_x, player_y, new_sword_candidate))
                    selecting_sword = False
                    new_sword_candidate = None
                elif inventory_open:
                    inventory_open = False

            elif event.key == pygame.K_TAB:
                if selecting_sword and new_sword_candidate:
                    sword_pickups.append(SwordPickup(player_x, player_y, new_sword_candidate))
                    selecting_sword = False
                    new_sword_candidate = None
                else:
                    inventory_open = not inventory_open

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # From chest
            if chest_ui_weapons:
                for idx, x_offset in enumerate([WIDTH // 2 - 480, WIDTH // 2, WIDTH // 2 + 480]):
                    box = pygame.Rect(x_offset, 200, 360, 600)

                    if box.collidepoint(mouse_x, mouse_y):
                        selected = chest_ui_weapons[idx]
                        # Spawn sword pickup on ground (from chest)
                        sword_pickups.append(SwordPickup(chest_being_opened.x, chest_being_opened.y, selected))
                        chest_ui_weapons = []
                        chest_being_opened = None
                        selecting_sword = False
                        break

            # From sword pickup replacement UI
            elif selecting_sword and new_sword_candidate:
                if sword_box1.collidepoint(mouse_x, mouse_y):
                    sword_pickups.append(SwordPickup(player_x, player_y, sword_1))
                    sword_1 = new_sword_candidate
                    selecting_sword = False
                    new_sword_candidate = None
                elif sword_box2.collidepoint(mouse_x, mouse_y):
                    sword_pickups.append(SwordPickup(player_x, player_y, sword_2))
                    sword_2 = new_sword_candidate
                    selecting_sword = False
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

    image = sword_images[current_sword.sword_type]
    sword_image = pygame.transform.scale(image, (120, 30))
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
                generate_new_sword(current_sword)

            if event.key == pygame.K_3 and player_ability_1:
                player_ability_1.try_activate()
            if event.key == pygame.K_4 and player_ability_2:
                player_ability_2.try_activate()


            if event.key == pygame.K_1:
                current_sword = sword_1
            if event.key == pygame.K_2:
                current_sword = sword_2
            if event.key == pygame.K_e and not selecting_sword:
                inventory_open = not inventory_open
            if event.key == pygame.K_TAB and not selecting_sword:
                inventory_open = not inventory_open



def dash():
    global player_x, player_y, is_dashing, dash_direction
    if is_dashing:
        player_x += dash_direction[0] * dash_speed * 7
        player_y += dash_direction[1] * dash_speed * 7
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
# Main loop
# Main loop
running = True
max_health, max_stamina = get_scaled_stats()
player_health = max_health
player_stamina = max_stamina
spawn_sword_timer = 0
spawn_sword_interval = 5000

while running:
    # 1. PRIDOBIMO DOGODKE samo enkrat
    events = pygame.event.get()

    # 2. Posredujemo dogodke vsem handlerjem

    # 2. Posredujemo dogodke vsem handlerjem
    handle_sword_pickup_events(events)
    handle_events(events)


    # 3. Če je meni (UI) odprt, ne izvajaj igre naprej
    if inventory_open or selecting_sword:
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

    current_time = pygame.time.get_ticks()
    if current_time - spawn_chest_timer > spawn_chest_interval:
        spawn_chest()
        spawn_chest_timer = current_time


    dash()

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= enemy_spawn_time:
        spawn_enemy()
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
                enemy_hit_timers[enemy.id] = current_time

                dx, dy = player_x - enemy.x, player_y - enemy.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist != 0:
                    player_knockback_direction = (dx / dist, dy / dist)
                    player_knockback = 1
                    player_knockback_velocity = 15

    
    for chest in chests:
        chest.draw()
        if chest.is_near_player() and not chest.opened:
            font = pygame.font.SysFont(None, 28)
            text = font.render("Press [F] to open chest", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 120, HEIGHT - 100))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_f]:
                chest.open()
                selecting_sword = True
                new_sword_candidate = None
                chest_ui_weapons = chest.weapons
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

    for pickup in sword_pickups:
        pickup.draw()

    for knife in knives:
        knife.update()
        knife.draw()
    knives = [k for k in knives if k.is_alive()]




    # Če izbiramo meč za zamenjavo, nariši UI
    if selecting_sword:
        draw_sword_selection_ui()
        pygame.display.flip()
        continue

    update_sword(player_draw_x, player_draw_y)
    draw_player(player_draw_x, player_draw_y)
    draw_stats()
    draw_custom_ui()
    draw_equipped_slots()



    pygame.display.flip()
    clock.tick(60)

pygame.quit()