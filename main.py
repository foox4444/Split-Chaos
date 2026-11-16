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
    {"world_width": 1600, "p1_spawn": (120, 620), "p2_spawn": (200, 620), "platforms": [pygame.Rect(0, 620, 450, 180), pygame.Rect(580, 560, 160, 25), pygame.Rect(830, 470, 160, 25), pygame.Rect(1100, 620, 500, 180)], "checkpoint": pygame.Rect(1480, 530, 60, 90)},
    {"world_width": 1800, "p1_spawn": (100, 620), "p2_spawn": (170, 620), "platforms": [pygame.Rect(0, 620, 350, 180), pygame.Rect(460, 530, 140, 25), pygame.Rect(700, 430, 140, 25), pygame.Rect(940, 530, 140, 25), pygame.Rect(1180, 420, 150, 25), pygame.Rect(1430, 620, 370, 180)], "checkpoint": pygame.Rect(1680, 530, 60, 90)},
    {"world_width": 2100, "p1_spawn": (90, 650), "p2_spawn": (150, 650), "platforms": [pygame.Rect(0, 650, 260, 150), pygame.Rect(380, 560, 110, 25), pygame.Rect(610, 460, 110, 25), pygame.Rect(840, 360, 110, 25), pygame.Rect(1080, 260, 120, 25), pygame.Rect(1340, 420, 100, 25), pygame.Rect(1580, 320, 100, 25), pygame.Rect(1800, 240, 300, 560)], "checkpoint": pygame.Rect(1980, 150, 60, 90)},
    {"world_width": 2400, "p1_spawn": (80, 620), "p2_spawn": (140, 620), "platforms": [pygame.Rect(0, 620, 220, 180), pygame.Rect(360, 540, 85, 25), pygame.Rect(590, 450, 85, 25), pygame.Rect(830, 520, 80, 25), pygame.Rect(1070, 420, 85, 25), pygame.Rect(1310, 320, 80, 25), pygame.Rect(1560, 450, 75, 25), pygame.Rect(1800, 360, 75, 25), pygame.Rect(2050, 270, 75, 25), pygame.Rect(2220, 220, 180, 580)], "checkpoint": pygame.Rect(2300, 130, 60, 90)},
    {"world_width": 2800, "p1_spawn": (70, 680), "p2_spawn": (130, 680), "platforms": [pygame.Rect(0, 680, 200, 120), pygame.Rect(340, 580, 70, 25), pygame.Rect(560, 480, 70, 25), pygame.Rect(790, 380, 65, 25), pygame.Rect(1030, 280, 65, 25), pygame.Rect(1280, 450, 65, 25), pygame.Rect(1520, 350, 60, 25), pygame.Rect(1760, 250, 60, 25), pygame.Rect(2010, 420, 60, 25), pygame.Rect(2260, 310, 60, 25), pygame.Rect(2500, 210, 60, 25), pygame.Rect(2640, 160, 160, 640)], "checkpoint": pygame.Rect(2710, 70, 60, 90)},
]

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
        
        # Checks if both players are at the checkpoint and if they are then it moves on to the next level
        if player1.rect.colliderect(level["checkpoint"]) and player2.rect.colliderect(level["checkpoint"]):
            current_level += 1
            if current_level >= len(LEVELS):
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
        
        pygame.display.flip()
        clock.tick(FPS)

# Main Menu Function
def main_menu():
    global click
    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        # Title in Main Menu
        draw_text('Split Chaos', font, (255, 255, 255), screen, 200, 50)
        
        # Button Stuff
        game_lever = pygame.Rect(400, 300, 200, 100)
        game_quit = pygame.Rect(400, 500, 200, 90)
        
        gl_color = (245, 235, 201) if game_lever.collidepoint((mx, my)) else (243, 230, 187)
        gq_color = (245, 235, 201) if game_quit.collidepoint((mx, my)) else (243, 230, 187)
        
        pygame.draw.rect(screen, gl_color, game_lever, border_radius=5)
        pygame.draw.rect(screen, gq_color, game_quit, border_radius=5)
        
        draw_text('Play', font, (243, 230, 187), screen, 420, 310)
        draw_text('Quit', font, (243, 230, 187), screen, 420, 510)
        
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