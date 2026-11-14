import pygame
from sys import exit
import random
import time
import os
import sys

#Pyinstaller Asset Helper:
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


#Variables
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
WORLD_WIDTH, WORLD_HEIGHT = 2400, 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Split Chaos")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)

GRAVITY = 0.8
JUMP_STR = -15
PLAYER_SPEED = 6
FLOOR_Y = 720
click = False

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, image_filename=None, target_height=60, fallback_size=(50, 50), fallback_color = "blue"):
        super().__init__()
        full_path = resource_path(image_filename) if image_filename else None
        if full_path and os.path.exists(full_path):
            raw_img = pygame.image.load(full_path).convert_alpha()
            orig_w, orig_h = raw_img.get_size()
            
            scale_ratio = target_height / orig_h
            new_width = int(orig_w * scale_ratio)
            self.base_image = pygame.transform.smoothscale(raw_img, (new_width, target_height))
        else:
            self.base_image = pygame.Surface(fallback_size, pygame.SRCALPHA)
            self.base_image.fill(fallback_color)
            pygame.draw.rect(self.base_image, BLACK, (0, 0, * fallback_size), 3)
        self.image = self.base_image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.controls = controls
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
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
    def update(self):
        self.image = (self.base_image if self.facing_right else pygame.transform.flip(self.base_image, True, False))
        self.rect.x += self.vel_x
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WORLD_WIDTH, self.rect.right)
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

def get_camera_rect(target_rect, view_width, view_height):
    cam_x = target_rect.centerx - view_width // 2
    cam_y = target_rect.centery - view_height // 2
    cam_x = max(0, min(cam_x, WORLD_WIDTH - view_width))
    cam_y = max(0, min(cam_y, WORLD_HEIGHT - view_height))
    return pygame.Rect(cam_x, cam_y, view_width, view_height)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def game_loop():
    world_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    
    p1_controls = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_w}
    p2_controls = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_UP}
    
    player1 = PLayer(120, FLOOR_Y, p1_controls, image_filename="banana_player.png", target_height = 64)
    player2 = Player(220, FLOOR_Y, p2_controls, image_filename="player2.png", target_height=52, fallback_size=(52, 52))
    all_players = pygame.sprite.Group(player1, player2)
    half_width = SCREEN_WIDTH // 2
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        keys = pygame.key.get_pressed()

def main_menu():
    global click
    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(0, 0, 0)
        draw_text('Split Chaos', font, (255, 255, 255), screen, 200, 50)
        
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
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game_lever.collidepoint(event.pos):
                        pass
                    if game_quit.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                        
        pygame.display.update()
        clock.tick(FPS)