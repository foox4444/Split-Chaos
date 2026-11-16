import pygame
from sys import exit
import random
import time
import os
import sys

# Pyinstaller Asset Helper:
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# Game Variables
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
WORLD_WIDTH, WORLD_HEIGHT = 2400, 800
FPS = 60

# Window Stuff
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Split Chaos")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)

# Variables
GRAVITY = 0.8
JUMP_STR = -15
PLAYER_SPEED = 6
FLOOR_Y = 720
click = False

# Creates the player's functions and controls
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, image_filename=None, target_height=60, fallback_size=(50, 50), fallback_color = "blue", flip_default = False):
        super().__init__()
        full_path = resource_path(image_filename) if image_filename else None
        if full_path and os.path.exists(full_path):
            raw_img = pygame.image.load(full_path).convert_alpha()
            orig_w, orig_h = raw_img.get_size()
            
            scale_ratio = target_height / orig_h
            new_width = int(orig_w * scale_ratio)
            self.base_image = pygame.transform.smoothscale(raw_img, (new_width, target_height))
        
            if flip_default:
                self.base_image = pygame.transform.flip(self.base_image, True, False)
        
        else:
            self.base_image = pygame.Surface(fallback_size, pygame.SRCALPHA)
            self.base_image.fill(fallback_color)
            pygame.draw.rect(self.base_image, "black", (0, 0, * fallback_size), 3)
        self.image = self.base_image
        self.spawn_pos = (x, y)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.controls = controls
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
    # Respawning Function
    def respawn(self):
        self.rect.midbottom = self.spawn_pos
        self.vel_x = 0
        self.vel_y = 0
    # Handles Controls
    def handle_input(self, keys):
        self.vel_x = 0
        if keys[self.controls["left"]]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[self.controls["right"]]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = JUMP_STR
            self.on_ground = False
    # Updates World
    def update(self, world_width, platforms):
        self.image = (self.base_image if self.facing_right else pygame.transform.flip(self.base_image, True, False))
        self.rect.x += self.vel_x
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(world_width, self.rect.right)
        
        # Platform Functions
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                elif self.vel_x < 0:
                    self.rect.left = plat.right
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground =False
        
        # More plat functions
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0
        
        if self.rect.top > WORLD_HEIGHT:
            self.respawn()

# Camera Functions
def get_camera_rect(target_rect, view_width, view_height, world_width):
    cam_x = target_rect.centerx - view_width // 2
    cam_y = target_rect.centery - view_height // 2
    cam_x = max(0, min(cam_x, world_width - view_width))
    cam_y = max(0, min(cam_y, WORLD_HEIGHT - view_height))
    return pygame.Rect(cam_x, cam_y, view_width, view_height)

# Text Function
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Creates Levels
LEVELS = [
    {"world_width": 1600, "p1_spawn": (120, 620), "p2_spawn": (200, 620), "platforms": [pygame.Rect(0, 620, 450, 180), pygame.Rect(580, 560, 160, 25), pygame.Rect(830, 470, 160, 25), pygame.Rect(1100, 620, 500, 180)], "checkpoint": pygame.Rect(1480, 530, 60, 90), "spikes": [],},
    {"world_width": 1800, "p1_spawn": (100, 620), "p2_spawn": (170, 620), "platforms": [pygame.Rect(0, 620, 350, 180), pygame.Rect(460, 530, 150, 25), pygame.Rect(700, 430, 180, 25), pygame.Rect(970, 530, 150, 25), pygame.Rect(1210, 430, 160, 25), pygame.Rect(1450, 620, 350, 180)], "checkpoint": pygame.Rect(1680, 530, 60, 90), "spikes": [pygame.Rect(765, 410, 45, 20)],},
    {"world_width": 2100, "p1_spawn": (90, 650), "p2_spawn": (150, 650), "platforms": [pygame.Rect(0, 650, 280, 150), pygame.Rect(380, 560, 140, 25), pygame.Rect(610, 460, 170, 25), pygame.Rect(870, 360, 140, 25), pygame.Rect(1100, 270, 170, 25), pygame.Rect(1360, 420, 140, 25), pygame.Rect(1590, 330, 140, 25), pygame.Rect(1800, 250, 300, 550)], "checkpoint": pygame.Rect(1980, 160, 60, 90), "spikes": [pygame.Rect(670, 440, 45, 20), pygame.Rect(1160, 250, 45, 20)],},
    {"world_width": 2400, "p1_spawn": (80, 620), "p2_spawn": (140, 620), "platforms": [pygame.Rect(0, 620, 250, 180), pygame.Rect(360, 540, 130, 25), pygame.Rect(580, 450, 160, 25), pygame.Rect(830, 520, 130, 25), pygame.Rect(1050, 430, 160, 25), pygame.Rect(1300, 340, 130, 25), pygame.Rect(1530, 450, 130, 25), pygame.Rect(1760, 360, 160, 25), pygame.Rect(2010, 280, 130, 25), pygame.Rect(2200, 230, 200, 570)], "checkpoint": pygame.Rect(2300, 140, 60, 90), "spikes": [pygame.Rect(635, 430, 45, 20), pygame.Rect(1105, 410, 45, 20), pygame.Rect(1815, 340, 45, 20)],},
    {"world_width": 2700, "p1_spawn": (70, 680), "p2_spawn": (130, 680), "platforms": [pygame.Rect(0, 680, 240, 120), pygame.Rect(340, 580, 120, 25), pygame.Rect(550, 490, 150, 25), pygame.Rect(790, 400, 120, 25), pygame.Rect(1010, 310, 150, 25), pygame.Rect(1260, 450, 120, 25), pygame.Rect(1480, 360, 120, 25), pygame.Rect(1700, 270, 150, 25), pygame.Rect(1950, 410, 120, 25), pygame.Rect(2170, 320, 150, 25), pygame.Rect(2400, 230, 120, 25), pygame.Rect(2560, 180, 140, 620)], "checkpoint": pygame.Rect(2610, 90, 60, 90), "spikes": [pygame.Rect(600, 470, 45, 20), pygame.Rect(1060, 290, 45, 20), pygame.Rect(1750, 250, 45, 20), pygame.Rect(2220, 300, 45, 20)],},
]


# Winning Screen Function
def win_screen(final_time=0.0):
    restart_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 310, 280, 65)
    menu_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 400, 280, 65)
    sub_font = pygame.font.SysFont(None, 36)

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn.collidepoint((mx, my)):
                    return "restart"
                if menu_btn.collidepoint((mx, my)):
                    return "menu"

        screen.fill("light blue")

        # 1. Title Banner
        title_surf = font.render("YOU WIN!", True, "gold")
        title_shadow = font.render("YOU WIN!", True, "black")
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_surf, title_rect)

        # 2. Subtitle Text
        sub_surf = sub_font.render("GOOD JOB Apple and Banana!", True, "black")
        screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 235)))
        time_surf = sub_font.render(f"Fina; Time: {final_time:.2f} seconds", True, "black")
        screen.blit(time_surf, time_surf.get_rect(center=(SCREEN_WIDTH // 2, 272)))

        # 3. Restart Button
        restart_color = (240, 80, 80) if restart_btn.collidepoint((mx, my)) else (210, 45, 45)
        pygame.draw.rect(screen, restart_color, restart_btn, border_radius=12)
        pygame.draw.rect(screen, "black", restart_btn, 3, border_radius=12)
        r_text = sub_font.render("Restart Game", True, "white")
        screen.blit(r_text, r_text.get_rect(center=restart_btn.center))

        # 4. Main Menu Button (Box first, then Text on top)
        menu_color = (245, 195, 50) if menu_btn.collidepoint((mx, my)) else (225, 170, 30)
        pygame.draw.rect(screen, menu_color, menu_btn, border_radius=12)
        pygame.draw.rect(screen, "black", menu_btn, 3, border_radius=12)
        m_text = sub_font.render("Main Menu", True, "black")
        screen.blit(m_text, m_text.get_rect(center=menu_btn.center))

        pygame.display.flip()
        clock.tick(FPS)



# Game Function
def game_loop():
    world_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    
    # Player 1 and 2 Controls
    p1_controls = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_w}
    p2_controls = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_UP}
    
    # Level Variables
    current_level = 0
    level = LEVELS[current_level]
    world_surface = pygame.Surface((level["world_width"], WORLD_HEIGHT))
    
    # Creates players with layered update
    player1 = Player(*level["p1_spawn"], p1_controls, image_filename="banana_player.png", target_height = 64)
    player2 = Player(*level["p2_spawn"], p2_controls, image_filename="apple_player.png", target_height=52, fallback_size=(52, 52), flip_default=True)
    all_players = pygame.sprite.LayeredUpdates(player1, player2)
    half_width = SCREEN_WIDTH // 2
    start_time = time.time()
    
    while True:
        for event in pygame.event.get():
            # Quitting Function
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        # Handles Keys Pressed
        keys = pygame.key.get_pressed()
        player1.handle_input(keys)
        player2.handle_input(keys)
        
        if player1.vel_x != 0 or player1.vel_y < 0:
            all_players.move_to_front(player1)
        if player2.vel_x != 0 or player2.vel_y < 0:
            all_players.move_to_front(player2)
        
        all_players.update(level["world_width"], level["platforms"])
        
        for spike in level.get("spikes", []):
            hitbox = spike.inflate(-8, -4)
            if player1.rect.colliderect(hitbox):
                player1.respawn()
            if player2.rect.colliderect(hitbox):
                player2.respawn()
        
        # Checks if both players are at the checkpoint and if they are then it moves on to the next level
        if player1.rect.colliderect(level["checkpoint"]) and player2.rect.colliderect(level["checkpoint"]):
            current_level += 1
            if current_level >= len(LEVELS):
                final_time = time.time() - start_time
                choice = win_screen(final_time)
                if choice == "restart":
                    current_level = 0
                    start_time = time.time()
                else:
                    return
            level = LEVELS[current_level]
            world_surface = pygame.Surface((level["world_width"], WORLD_HEIGHT))
            player1.spawn_pos = level["p1_spawn"]
            player2.spawn_pos = level["p2_spawn"]
            player1.respawn()
            player2.respawn()
        
        world_surface.fill("light blue")

        for x in range(100, level["world_width"], 250):
            pygame.draw.circle(world_surface, "white", (x, 140), 30)
            pygame.draw.circle(world_surface, "white", (x+25, 130), 38)
            pygame.draw.circle(world_surface, "white", (x+55, 140), 30)
            
        for plat in level["platforms"]:
            pygame.draw.rect(world_surface, (110, 75, 45), plat)
            pygame.draw.rect(world_surface,(50, 185, 75), (plat.x, plat.y, plat.width, 12))
            pygame.draw.rect(world_surface, "black", plat, 2)
        
        pygame.draw.rect(world_surface, (25, 15, 35), (0, WORLD_HEIGHT - 25, level["world_width"], 25),)

        for spike in level.get("spikes", []):
            for sx in range(spike.left, spike.right - 9, 15):
                points = [(sx, spike.bottom), (sx + 7, spike.top), (sx + 15, spike.bottom),]
                pygame.draw.polygon(world_surface, (220, 35, 45), points)
                pygame.draw.polygon(world_surface, "black", points, 2)

        pygame.draw.rect(world_surface, "gold", level["checkpoint"], border_radius=8)
        pygame.draw.rect(world_surface, "black", level["checkpoint"], 3, border_radius=8)
        
        all_players.draw(world_surface)

        # Camera Variables
        cam1 = get_camera_rect(player1.rect, half_width, SCREEN_HEIGHT, level["world_width"])
        cam2 = get_camera_rect(player2.rect, half_width, SCREEN_HEIGHT, level["world_width"])
        
        # Making the Screen
        screen.blit(world_surface, (0, 0), cam1)
        screen.blit(world_surface, (half_width, 0), cam2)
        pygame.draw.line(screen, "black", (half_width, 0), (half_width, SCREEN_HEIGHT), 4)
        draw_text(f"Level {current_level +1}", font, "black", screen, 20, 20)
        elapsed = time.time() - start_time
        draw_text(f"Time: {elapsed:.1f}s", font, "black", screen, SCREEN_WIDTH - 260, 20)
        
        pygame.display.flip()
        clock.tick(FPS)

# Main Menu Function
def main_menu():
    global click
    
    bg_path = resource_path("menu_bg.jpg")
    if os.path.exists(bg_path):
        menu_bg = pygame.image.load(bg_path).convert()
        menu_bg = pygame.transform.smoothscale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        menu_bg = None
    
    while True:
        mx, my = pygame.mouse.get_pos()
        screen.blit(menu_bg, (0, 0))
        # Title in Main Menu
        title_box = pygame.Surface((420, 90), pygame.SRCALPHA)
        pygame.draw.rect(title_box, (20, 22, 30, 215), (0, 0, 420, 90), border_radius=16)
        pygame.draw.rect(title_box, (255, 215, 60), (0, 0, 420, 90), 3, border_radius=16)
        screen.blit(title_box, (SCREEN_WIDTH // 2 -210, 45))
        title_surf = font.render('Split Chaos', True, (255, 255, 255))
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 90)))
        
        # Button Stuff
        game_lever = pygame.Rect(400, 300, 200, 100)
        game_quit = pygame.Rect(400, 500, 200, 90)
        
        gl_color = (38, 72, 58) if game_lever.collidepoint((mx, my)) else (22, 28, 36)
        gq_color = (85, 35, 45) if game_quit.collidepoint((mx, my)) else (22, 28, 36)
        pygame.draw.rect(screen, gl_color, game_lever, border_radius=5)
        pygame.draw.rect(screen, (90, 210, 130), game_lever, 3, border_radius=12)
        pygame.draw.rect(screen, gq_color, game_quit, border_radius=5)
        pygame.draw.rect(screen, (235, 95, 105), game_quit, 3, border_radius=12)
        
        play_surf = font.render('Play', True, (255, 255, 255))
        quit_surf = font.render('Quit', True, (255, 255, 255))
        screen.blit(play_surf, play_surf.get_rect(center=game_lever.center))
        screen.blit(quit_surf, quit_surf.get_rect(center=game_quit.center))
        
        click = False
        for event in pygame.event.get():
            # Quit Function
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Following out Button functions
                if event.button == 1:
                    if game_lever.collidepoint(event.pos):
                        game_loop()
                    if game_quit.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                        
        pygame.display.update()
        clock.tick(FPS)
if __name__ == "__main__":
    main_menu()