import pygame as pg
import time
from sys import exit
from random import choice
from FlaPyBird.constants import *


def animation():
    global speedy_active

    new_powerUp2 = powerUp2_frames[powerUp2_index]
    new_powerUp2_rect = new_powerUp2.get_rect(center=(powerUp_rect.centerx, powerUp_rect.centery))
    
    if speedy_active == False:
        new_bird = bird_frames[bird_index]
        new_bird_rect = new_bird.get_rect(center=(50, bird_rect.centery))
        
    if speedy_active == True:
        new_bird = bird_speedy_frames[bird_index]
        new_bird_rect = new_bird.get_rect(center=(50, bird_rect.centery))


    return new_bird, new_bird_rect, new_powerUp2, new_powerUp2_rect


def create_pipe():
    random_pipe = choice(pipe_hei)
    top_pipe = pipe.get_rect(midbottom=(DISPLAY_WIDTH + 26, random_pipe - 150))
    bottom_pipe = pipe.get_rect(midtop=(DISPLAY_WIDTH + 26, random_pipe))

    return top_pipe, bottom_pipe


def draw_pipe(pipes):
    for p in pipes:
        if p.bottom >= DISPLAY_HEIGHT:
            display.blit(pipe, p)
        else:
            flip_pipe = pg.transform.flip(pipe, False, True)
            display.blit(flip_pipe, p)


def move_pipe(pipes):
    for p in pipes:
        p.centerx -= pipe_speed

    return pipes


def spawn_pipe():
    if event.type == pipe_spawn:
        pipe_list.append(create_pipe())


def remove_pipe(pipes):
    global obstacle_number

    if len(pipes) != 0:
        if pipes[0][0] + 52 <= 0:
            pipes.pop(0)
            pipes.pop(0)
            obstacle_number -= 2
    
    return pipes[:]


def move_floor():
    for i in range(3):
        display.blit(floors[i], (floor_pos_x[i], DISPLAY_HEIGHT - floor_rects[i].height // 2))
        display.blit(floors[i], (floor_pos_x[i] + DISPLAY_WIDTH, DISPLAY_HEIGHT - floor_rects[i].height // 2))


def check_obstacle_passed():
    global obstacle_number
    pipes = pipe_list[:]

    if len(pipes) > obstacle_number:
        if pipes[obstacle_number][0] + 52 <= 26:
            obstacle_number += 2
            point_snd.play()
            return True

    return False


def check_collision(pipes):
    for p in pipes:
        if bird_rect.colliderect(p):
            collide_snd.play()
            return False

    for i in range(3):
        if bird_rect.top <= 0 or bird_rect.bottom >= DISPLAY_HEIGHT - floor_rects[i].height // 2:
            collide_snd.play()
            return False

    return True
    
    
def create_powerUp(type):
    random_pu_pos = choice(powerUp_height)
    global currentPU_type	# use the global power-up type variable
    
    if type == 1:		# create type corresponding to argument (change powerUp1, powerUp2, etc befote .get_rect)
        powerUp_rect_object = powerUp1.get_rect(center=(DISPLAY_WIDTH + 220, (DISPLAY_HEIGHT // 2) + random_pu_pos))
        currentPU_type = 1        
    if type == 2:
        powerUp_rect_object = powerUp2.get_rect(center=(DISPLAY_WIDTH + 220, (DISPLAY_HEIGHT // 2) + random_pu_pos))
        currentPU_type = 2
    if type == 3:
        powerUp_rect_object = powerUp3.get_rect(center=(DISPLAY_WIDTH + 220, (DISPLAY_HEIGHT // 2) + random_pu_pos))
        currentPU_type = 3 
    
    return powerUp_rect_object
    
    
def draw_powerUp(powerUp_rect_obj):	# display the PowerUps
    if currentPU_type == 1:
        display.blit(powerUp1, powerUp_rect_obj)	# first argument varies depending on currently-active PowerUp
    if currentPU_type == 2:
        display.blit(powerUp2, powerUp_rect_obj)
    if currentPU_type == 3:
        display.blit(powerUp3, powerUp_rect_obj)
                
                
def move_powerUp(powerUp_rect_obj): 
    powerUp_rect_obj.centerx -= pipe_speed	# determines how fast the power-up moves across the screen
    
    return powerUp_rect_obj


# Checks for power up collision, moves them out of screen
def check_collision_pu(power_up, p_ups_active):
    if bird_rect.colliderect(power_up):
        global start_ticks
        global powerUp_active  # is the power up active?
        start_ticks = pg.time.get_ticks()
        power_up.center = (1, 512)
        # Pass a string based on the name of the power up
        if currentPU_type == 1:	# check which type of PowerUp is currently active 
            activate_pu("speed", p_ups_active)
            powerUp_active = True
            p_ups_active[0] = True
        if currentPU_type == 2:
            activate_pu("space", p_ups_active)
            powerUp_active = True
            p_ups_active[1] = True
        if currentPU_type == 3:	# check which type of PowerUp is currently active 
            activate_pu("slow", p_ups_active)
            powerUp_active = True
            p_ups_active[2] = True
        return 1
    return 0


# Can set different values depending on power up
def activate_pu(pu_name, p_ups_active):
    if pu_name == "speed":
        deactivate_pu(3, p_ups_active)  # Preemptively deactivating power ups
        deactivate_pu(2, p_ups_active)
        global speed_multiplier
        global speedy_active
        speedy_active = True
        speed_multiplier = 2.0
    if pu_name == "space":
        deactivate_pu(3, p_ups_active)	# ensures speed and spacing does not break by activating another PU
        deactivate_pu(1, p_ups_active)  # Deactivate the other power up to ensure that only one is active at the same time
        global pipe_spacing
        pipe_spacing = 8000
    if pu_name == "slow":
        deactivate_pu(2, p_ups_active)	# ditto as above
        deactivate_pu(1, p_ups_active)
        global pipe_speed
        global pipe_speed_store
        pipe_speed_store = pipe_speed
        pipe_speed -= 2.0


# Set all values affected by power ups to default
def deactivate_pu(type, p_ups_active):
    if type == 1:
        p_ups_active[0] = False
        global speed_multiplier
        global speedy_active
        speedy_active = False
        speed_multiplier = 1.0
    if type == 2:
        p_ups_active[1] = False
        global pipe_spacing
        pipe_spacing = 6000
    if type == 3:
        p_ups_active[2] = False
        global pipe_speed
        global pipe_speed_store
        pipe_speed = pipe_speed_store
    

def score_display(game_state):
    if game_state == 'main_game':
        score_font = font.render(str(int(score)), True, white)
        score_font_rect = score_font.get_rect(center=(DISPLAY_WIDTH // 2, 50))
        display.blit(score_font, score_font_rect)

        pu_score_font = font.render(str(int(pu_score)), True, yellow)
        pu_score_font_rect = pu_score_font.get_rect(center=(DISPLAY_WIDTH // 2 + 75, 50))
        display.blit(pu_score_font, pu_score_font_rect)
    elif game_state == 'game_over':
        score_font = font.render(f'Score: {int(score)}', True, white)
        score_font_rect = score_font.get_rect(center=(DISPLAY_WIDTH // 2, 50))
        display.blit(score_font, score_font_rect)

        pu_score_font = font.render(f'Power Up Score: {int(pu_score)}', True, yellow)
        pu_score_font_rect = pu_score_font.get_rect(center=(DISPLAY_WIDTH // 2, 80))
        display.blit(pu_score_font, pu_score_font_rect)

        hight_score_font = font.render(f'High Score: {int(high_score)}', True, white)
        hight_score_font_rect = hight_score_font.get_rect(center=(DISPLAY_WIDTH // 2, 412))
        display.blit(hight_score_font, hight_score_font_rect)

        pu_hight_score_font = font.render(f'Power Up High Score: {int(pu_high_score)}', True, yellow)
        pu_hight_score_font_rect = pu_hight_score_font.get_rect(center=(DISPLAY_WIDTH // 2, 442))
        display.blit(pu_hight_score_font, pu_hight_score_font_rect)


def display_active_power_ups(p_ups_active):
    if p_ups_active[0]:
        pu_rect = powerUp1.get_rect(center=(DISPLAY_WIDTH // 2 - 225, 50))
        display.blit(powerUp1, pu_rect)
    if p_ups_active[1]:
        pu_rect = powerUp2.get_rect(center=(DISPLAY_WIDTH // 2 - 150, 50))
        display.blit(powerUp2, pu_rect)
    if p_ups_active[2]:
        pu_rect = powerUp3.get_rect(center=(DISPLAY_WIDTH // 2 - 75, 50))
        display.blit(powerUp3, pu_rect)


def increment_score(scr, increment):
    if check_obstacle_passed():
        return scr + increment

    return scr


def score_update(scr, high_scr, pu_scr, pu_high_scr):
    if scr > high_scr:
        high_scr = scr
    if pu_scr > pu_high_scr:
        pu_high_scr = pu_scr

    return high_scr, pu_high_scr


'DISPLAY'
display = pg.display.set_mode(DISPLAY_AREA)
pg.display.set_caption('FlaPyBird')

'BACKGROUND'
bg = pg.image.load('assets/images/sprites/Background.png').convert()
floors = []
floor_pos_x = [0, 288, 576]
floor_rects = []
for i in range(3):
    floors.append(pg.image.load('assets/images/sprites/Floor.png').convert_alpha())
    floor_rects.append(floors[i].get_rect())

pipe = pg.image.load('assets/images/sprites/Pipe.png')
pipe_list = []
pipe_spawn = pg.USEREVENT
obstacle_number = 0

pipe_speed = 3
pipe_speed_store = 3
pipe_spacing = 6000
pg.time.set_timer(pipe_spawn, int(pipe_spacing / pipe_speed))	# delay between spawning another pipe 
pipe_hei = [200, 300, 400]
bg_game_over = pg.image.load('assets/images/sprites/Game_Over.png')
bg_game_over_rect = bg_game_over.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 25))

'BIRD'
bird_down = pg.image.load('assets/images/sprites/Bird_down.png').convert_alpha()
bird_mid = pg.image.load('assets/images/sprites/Bird_mid.png').convert_alpha()
bird_up = pg.image.load('assets/images/sprites/Bird_up.png').convert_alpha()
bird_frames = [bird_down, bird_mid, bird_up]

bird_down_speedy = pg.image.load('assets/images/sprites/Bird_down_speedy.png').convert_alpha()
bird_mid_speedy = pg.image.load('assets/images/sprites/Bird_mid_speedy.png').convert_alpha()
bird_up_speedy = pg.image.load('assets/images/sprites/Bird_up_speedy.png').convert_alpha()
bird_speedy_frames = [bird_down_speedy, bird_mid_speedy, bird_up_speedy]

bird_index = 0
bird = bird_frames[bird_index]
bird_rect = bird.get_rect(center=(50, DISPLAY_HEIGHT // 2))

speedy_active = False
bird_speedy = bird_speedy_frames[bird_index]
bird_speedy_rect = bird_speedy.get_rect(center=(50, DISPLAY_HEIGHT // 2))

bird_flap = pg.USEREVENT + 1
pg.time.set_timer(bird_flap, 200)
bird_move = 0.0
bird_rotate = 0
bird_moving_up = False
bird_moving_down = False

'POWER-UP'
powerUp1 = pg.image.load('assets/images/sprites/lightning.png').convert_alpha() 
powerUp2_frames = [pg.image.load('assets/images/sprites/R_Pickup_1.png.png').convert_alpha(),
                   pg.image.load('assets/images/sprites/R_Pickup_2.png.png').convert_alpha(),
                   pg.image.load('assets/images/sprites/R_Pickup_3.png.png').convert_alpha()]
powerUp3 = pg.image.load('assets/images/sprites/clock_icon.png').convert_alpha()
powerUp2 = powerUp2_frames[0]
powerUp2_index = 0
powerUp_types = [1, 2, 3]
currentPU_type = 1		# default to 1, changed when new ones spawned 
powerUp_duration = 5		# default to 5, changes according to last power-up created

powerUp_spawn = pg.USEREVENT
powerUp_spawn_counter = 0	# counter used to determine when to spawn a power-up
powerUp_height = [-100, 0, 100]
powerUp_rect = powerUp1.get_rect(center=(DISPLAY_WIDTH + 20, DISPLAY_HEIGHT // 2))
powerUp_active = False  # is there an active power up?
p_ups_active = [False, False, False]
start_ticks = 0  # start_ticks starts the timer for the power up
speed_multiplier = 1.0

'SOUND EFFECTS'
pg.mixer.init(44100, 16, 2, 512)
flap_snd = pg.mixer.Sound('assets/sounds/sound_effects/Flap.ogg')
collide_snd = pg.mixer.Sound('assets/sounds/sound_effects/Hit.ogg')
point_snd = pg.mixer.Sound('assets/sounds/sound_effects/Point.ogg')

'FONT'
pg.font.init()
font = pg.font.Font('assets/font/04B_19.ttf', 20)

'SCORE'
high_score = 0
score = high_score
pu_score = 0
pu_high_score = pu_score

'FPS'
clock = pg.time.Clock()
fps = 60

'LOOP'
game = True
while True:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP or event.key == pg.K_w:
                bird_moving_up = True
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                bird_moving_down = True
            if event.key == pg.K_SPACE and not game:
                game = True
                pipe_list.clear()
                bird_move = 0.0
                bird_rect.center = (50, DISPLAY_HEIGHT // 2)
                score = 0
                pu_score = 0
                obstacle_number = 0
                pipe_speed = 3

        if event.type == pg.KEYUP:
            if event.key == pg.K_UP or event.key == pg.K_w:
                bird_moving_up = False
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                bird_moving_down = False

        if event.type == bird_flap: #  Also used for power up animations
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            if powerUp2_index < 2:
                powerUp2_index += 1
            else:
                powerUp2_index = 0

            bird, bird_rect, powerUp2, powerUp_rect = animation()


        if event.type == pipe_spawn:
            pipe_list.extend(create_pipe())
            powerUp_spawn_counter += 1
            if pipe_speed <= 4:
                pipe_speed += 0.125
            elif pipe_speed <= 6:
                pipe_speed += 0.1
            elif pipe_speed <= 8:
                pipe_speed += 0.075
            else:
                pipe_speed += 0.05
            pg.time.set_timer(pipe_spawn, int(pipe_spacing / pipe_speed))
            
        if event.type == powerUp_spawn:
            if powerUp_spawn_counter % 5 == 0:	# this adjusts how frequently power-ups will spawn
                random_pu_type = choice(powerUp_types)
                powerUp_rect = create_powerUp(random_pu_type)
                powerUp_spawn_counter = 0

    # Bird movement
    if bird_moving_up and bird_moving_down:
        bird_move = 0.0
        bird_rotate = 0
    elif bird_moving_up:
        bird_move = -4.0 * speed_multiplier
        bird_rotate = 20
    elif bird_moving_down:
        bird_move = 4.0 * speed_multiplier
        bird_rotate = -20
    else:
        bird_move = 0.0
        bird_rotate = 0

    display.blit(bg, (0, 0))
    display.blit(bg, (288, 0))
    display.blit(bg, (576, 0))

    if game:
        # BIRD
        bird_rect.centery += float(bird_move)

        display.blit(pg.transform.rotate(bird, bird_rotate), bird_rect)
        game = check_collision(pipe_list)
        pu_score += check_collision_pu(powerUp_rect, p_ups_active)  # checks for collision with power up
        if powerUp_active:
            seconds = (pg.time.get_ticks() - start_ticks) / 1000  # calculate how many seconds
            if seconds > powerUp_duration:  # if more than 5 seconds, then clear the power up
                # This function sets all the power up effects back to default values
                deactivate_pu(currentPU_type, p_ups_active)
                powerUp_active = False

        # PIPE
        draw_pipe(pipe_list)
        pipe_list = move_pipe(pipe_list)
        pipe_list = remove_pipe(pipe_list)
        
        # POWER-UP
        draw_powerUp(powerUp_rect)
        powerUp_rect = move_powerUp(powerUp_rect)

        # SCORE
        score_display('main_game')
        score = increment_score(score, 1)

        # ACTIVE POWER-UPS
        display_active_power_ups(p_ups_active)
    else:
        deactivate_pu(currentPU_type, p_ups_active)
        display.blit(bg_game_over, bg_game_over_rect)

        # PIPE
        pipe_list = move_pipe(pipe_list)
        pipe_list = remove_pipe(pipe_list)
        
        # POWER-UP
        powerUp_rect = move_powerUp(powerUp_rect)
        
        # SCORE
        high_score, pu_high_score = score_update(score, high_score, pu_score, pu_high_score)
        score_display('game_over')

    # FLOOR
    move_floor()
    for i in range(3):
        if floor_pos_x[i] <= -DISPLAY_WIDTH:
            floor_pos_x[i] = 0
        floor_pos_x[i] -= 1

    pg.display.update()
