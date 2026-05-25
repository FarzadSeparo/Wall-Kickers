import pygame
import sys
import os
import random

pygame.init()

WIDTH = 500
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wall Kickers - pygame ")
clock = pygame.time.Clock()

# =====================
# IMAGES & ASSETS
# =====================
def load_and_scale(filename, size):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    print(f"هشدار: فایل '{filename}' پیدا نشد!")
    return None

P_SIZE = (50, 50)

monkey_states = {
    "stand_left": load_and_scale("img/Monkey-standing-left.png", P_SIZE),
    "stand_right": load_and_scale("img/Monkey-standing-upright.png", P_SIZE),
    "jump_left": load_and_scale("img/Monkey-Jump-Left.png", P_SIZE),
    "jump_right": load_and_scale("img/Monkey-Jump-Right.png", P_SIZE),
    "hang_left": load_and_scale("img/Monkey-Hanging-Left.png", P_SIZE),
    "hang_right": load_and_scale("img/Monkey-Hanging-Right.png", P_SIZE)
}

use_player_images = all(img is not None for img in monkey_states.values())

bg_filename = "img/background.png"
if os.path.exists(bg_filename):
    raw_bg = pygame.image.load(bg_filename).convert()
    BACKGROUND_IMG = pygame.transform.scale(raw_bg, (WIDTH, HEIGHT))
    use_bg_image = True
else:
    use_bg_image = False
bg_y1, bg_y2 = 0, -HEIGHT

track_filename = "img/track.png"
LEFT_WALL_X, RIGHT_WALL_X, WALL_WIDTH = 120, WIDTH - 140, 20
TRACK_X = LEFT_WALL_X + WALL_WIDTH - 55
TRACK_WIDTH = RIGHT_WALL_X - TRACK_X + 50

if os.path.exists(track_filename):
    raw_track = pygame.image.load(track_filename).convert_alpha()
    TRACK_IMG = pygame.transform.scale(raw_track, (TRACK_WIDTH, HEIGHT))
    use_track_image = True
else:
    use_track_image = False
track_y1, track_y2 = 0, -HEIGHT

wall_filename = "img/wall.png"
if os.path.exists(wall_filename):
    WALL_SRC_IMG = pygame.image.load(wall_filename).convert_alpha()
    use_wall_image = True
else:
    use_wall_image = False

# =====================
# COLORS & CONFIG
# =====================
ORANGE = (255, 140, 0) 
GREEN = (60, 200, 120) 
BROWN = (120, 70, 40)
PLAYER_COLOR = (255, 255, 255)

# =====================
# FIXED LEVEL DESIGN (تنظیم دقیق ابعاد برای صعود راحت)
# =====================
left_walls = []
right_walls = []
highest_wall_y = HEIGHT - 40 

def generate_wall_pair(is_start=False):
    global highest_wall_y
    
    if is_start:
        # دیوارهای بخش شروع بازی کاملاً بلند هستند تا بازیکن راحت بالا برود
        left_height = 250
        right_height = 250
        vertical_gap = 60
    else:
        # دیوارهای بالاتر: طول بلندتر (۱۶) تا ۲۴۰) و فاصله‌ی عمودی بسیار کم و ایمن (۶۰ تا ۸۰)
        left_height = random.randint(160, 240)
        right_height = random.randint(160, 240)
        vertical_gap = random.randint(60, 80)
    
    max_height = max(left_height, right_height)
    highest_wall_y = highest_wall_y - max_height - vertical_gap
    
    left_walls.append(pygame.Rect(LEFT_WALL_X, highest_wall_y, WALL_WIDTH, left_height))
    right_walls.append(pygame.Rect(RIGHT_WALL_X, highest_wall_y, WALL_WIDTH, right_height))

# تولید دیوارهای اولیه (۳ تای اول کاملاً بلند و ساده برای شروع راحت)
for i in range(10):
    generate_wall_pair(is_start=(i < 3))

# =====================
# PLAYER STATE VARIABLES
# =====================
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 100, P_SIZE[0], P_SIZE[1])
vel_x = 0
vel_y = 0

GRAVITY = 0.30       
JUMP_POWER = -11     
KICK_SPEED = 11      

on_left = False
on_right = False
is_kicking = False   
on_wall_top = False  

last_direction = "right"  
current_sprite = "stand_right"

camera_y = 0
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # =====================
    # CLASSIC CONTROLS
    # =====================
    if not is_kicking:
        if keys[pygame.K_LEFT]:
            vel_x = -3.5
            last_direction = "left"
        elif keys[pygame.K_RIGHT]:
            vel_x = 3.5
            last_direction = "right"
        else:
            vel_x *= 0.85 
    else:
        vel_x *= 0.97 
        if abs(vel_x) < 2: 
            is_kicking = False 

    if keys[pygame.K_LEFT] and on_right:
        vel_x = -KICK_SPEED
        vel_y = JUMP_POWER
        is_kicking = True
        on_right = False
        last_direction = "left"

    if keys[pygame.K_RIGHT] and on_left:
        vel_x = KICK_SPEED
        vel_y = JUMP_POWER
        is_kicking = True
        on_left = False
        last_direction = "right"

    # =====================
    # PHYSICS & COLLISIONS
    # =====================
    vel_y += GRAVITY

    on_left = False
    on_right = False
    on_wall_top = False

    all_walls = left_walls + right_walls

    # حرکت افقی
    player.x += int(vel_x)
    for wall in all_walls:
        if player.colliderect(wall):
            if vel_x > 0: 
                player.right = wall.left
                vel_x = 0
                is_kicking = False 
                if wall in right_walls:
                    on_right = True
            elif vel_x < 0: 
                player.left = wall.right
                vel_x = 0
                is_kicking = False
                if wall in left_walls:
                    on_left = True

    # حرکت عمودی
    player.y += int(vel_y)
    for wall in all_walls:
        if player.colliderect(wall):
            if vel_y > 0: 
                player.bottom = wall.top
                vel_y = 0
                on_wall_top = True
            elif vel_y < 0: 
                player.top = wall.bottom
                vel_y = 0

    if (on_left or on_right) and vel_y > 0:
        vel_y = 0.5 

    # =====================
    # CAMERA & INFINITE
    # =====================
    if player.y < HEIGHT // 2:
        shift_y = (HEIGHT // 2) - player.y
        player.y = HEIGHT // 2
        
        for wall in left_walls + right_walls:
            wall.y += shift_y
        highest_wall_y += shift_y 
        
        if use_bg_image:
            bg_y1 += shift_y
            bg_y2 += shift_y
            if bg_y1 >= HEIGHT: bg_y1 = bg_y2 - HEIGHT
            if bg_y2 >= HEIGHT: bg_y2 = bg_y1 - HEIGHT
        if use_track_image:
            track_y1 += shift_y
            track_y2 += shift_y
            if track_y1 >= HEIGHT: track_y1 = track_y2 - HEIGHT
            if track_y2 >= HEIGHT: track_y2 = track_y1 - HEIGHT
        camera_y += shift_y

    if highest_wall_y > -300:
        generate_wall_pair(is_start=False)

    left_walls = [w for w in left_walls if w.y < HEIGHT + 200]
    right_walls = [w for w in right_walls if w.y < HEIGHT + 200]

    # =====================
    # BOUNDARIES & BOUNCE
    # =====================
    if player.left < 0:
        player.left = 0
        vel_x = 0
    if player.right > WIDTH:
        player.right = WIDTH
        vel_x = 0

    if player.bottom > HEIGHT:
        player.bottom = HEIGHT
        vel_y = JUMP_POWER  
        on_wall_top = True
        is_kicking = False

    if on_wall_top:
        vel_y = JUMP_POWER 

    # =====================
    # ANIMATION LOGIC
    # =====================
    if on_left:
        current_sprite = "hang_left"
    elif on_right:
        current_sprite = "hang_right"  
    elif on_wall_top and vel_y == 0:
        if last_direction == "left":
            current_sprite = "stand_left"
        else:
            current_sprite = "stand_right"
    else:
        if vel_x < 0 or last_direction == "left":
            current_sprite = "jump_left"
        else:
            current_sprite = "jump_right"

    # =====================
    # DRAW
    # =====================
    if use_bg_image:
        screen.blit(BACKGROUND_IMG, (0, bg_y1))
        screen.blit(BACKGROUND_IMG, (0, bg_y2))
    else:
        screen.fill(ORANGE)

    if use_track_image:
        screen.blit(TRACK_IMG, (TRACK_X, track_y1))
        screen.blit(TRACK_IMG, (TRACK_X, track_y2))
    else:
        pygame.draw.rect(screen, GREEN, (LEFT_WALL_X, 0, RIGHT_WALL_X - LEFT_WALL_X + WALL_WIDTH, HEIGHT))

    for wall in left_walls + right_walls:
        if use_wall_image:
            scaled_wall_img = pygame.transform.scale(WALL_SRC_IMG, (wall.width, wall.height))
            screen.blit(scaled_wall_img, (wall.x, wall.y))
        else:
            pygame.draw.rect(screen, BROWN, wall)

    if use_player_images:
        screen.blit(monkey_states[current_sprite], (player.x, player.y))
    else:
        pygame.draw.rect(screen, PLAYER_COLOR, player)

    pygame.display.flip()


    # telegram : @Mr_Separo

