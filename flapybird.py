import pygame as pg
import time
from sys import exit
from random import choice
from FlaPyBird.constants import *


def animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(50, bird_rect.centery))

    return new_bird, new_bird_rect


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
            # point_snd.play()
            return True

    return False


def check_collision(pipes):
    for p in pipes:
        if bird_rect.colliderect(p):
            # collide_snd.play()
            return False

    for i in range(3):
        if bird_rect.top <= 0 or bird_rect.bottom >= DISPLAY_HEIGHT - floor_rects[i].height // 2:
            # collide_snd.play()
            return False

    return True
    
    
def create_powerUp():
    random_pu_pos = choice(powerUp_height)
    powerUp_rect_object = powerUp.get_rect(center=(DISPLAY_WIDTH + 220, (DISPLAY_HEIGHT // 2) + random_pu_pos))
    
    return powerUp_rect_object
    
    
def draw_powerUp(powerUp_rect_obj):
    display.blit(powerUp, powerUp_rect_obj)
                
                
def move_powerUp(powerUp_rect_obj): 
    powerUp_rect_obj.centerx -= pipe_speed	# determines how fast the power-up moves across the screen
    
    return powerUp_rect_obj


# Checks for power up collision, moves them out of screen
def check_collision_pu(power_up):
    if bird_rect.colliderect(power_up):
        global start_ticks
        global powerUp_active  # is the power up active?
        start_ticks = pg.time.get_ticks()
        power_up.center = (1, 512)
        # Pass a string based on the name of the power up
        activate_pu("speed")
        powerUp_active = True


# Can set different values depending on power up
def activate_pu(pu_name):
    if pu_name == "speed":
        global speed_multiplier
        speed_multiplier = 1.5


# Set all values affected by power ups to default
def deactivate_pu():
    global speed_multiplier
    speed_multiplier = 1.0


def score_display(game_state):
    if game_state == 'main_game':
        score_font = font.render(str(int(score)), True, white)
        score_font_rect = score_font.get_rect(center=(DISPLAY_WIDTH // 2, 50))
        display.blit(score_font, score_font_rect)
    elif game_state == 'game_over':
        score_font = font.render(f'Score: {int(score)}', True, white)
        score_font_rect = score_font.get_rect(center=(DISPLAY_WIDTH // 2, 50))
        display.blit(score_font, score_font_rect)

        hight_score_font = font.render(f'High Score: {int(high_score)}', True, white)
        hight_score_font_rect = hight_score_font.get_rect(center=(DISPLAY_WIDTH // 2, 412))
        display.blit(hight_score_font, hight_score_font_rect)


def increment_score(scr, increment):
    if check_obstacle_passed():
        return scr + increment

    return scr


def score_update(scr, high_scr):
    if scr > high_scr:
        high_scr = scr

    return high_scr


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
pg.time.set_timer(pipe_spawn, int(6000 / pipe_speed))
pipe_hei = [200, 300, 400]
bg_game_over = pg.image.load('assets/images/sprites/Game_Over.png')
bg_game_over_rect = bg_game_over.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 25))

'BIRD'
bird_down = pg.image.load('assets/images/sprites/Bird_down.png').convert_alpha()
bird_mid = pg.image.load('assets/images/sprites/Bird_mid.png').convert_alpha()
bird_up = pg.image.load('assets/images/sprites/Bird_up.png').convert_alpha()
bird_frames = [bird_down, bird_mid, bird_up]
bird_index = 0
bird = bird_frames[bird_index]
bird_rect = bird.get_rect(center=(50, DISPLAY_HEIGHT // 2))
bird_flap = pg.USEREVENT + 1
pg.time.set_timer(bird_flap, 200)
bird_move = 0.0
bird_rotate = 0

'POWER-UP'
powerUp = pg.image.load('assets/images/sprites/lightning.png').convert_alpha()		# replace with different file later 
powerUp_spawn = pg.USEREVENT
powerUp_spawn_counter = 0	# counter used to determine when to spawn a power-up
powerUp_height = [-100, 0, 100]
powerUp_rect = powerUp.get_rect(center=(DISPLAY_WIDTH + 20, DISPLAY_HEIGHT // 2))
powerUp_active = False  # is there an active power up?
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
                bird_move = -4.0 * speed_multiplier
                bird_rotate = 20
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                bird_move = 4.0 * speed_multiplier
                bird_rotate = -20
            if event.key == pg.K_SPACE and not game:
                game = True
                pipe_list.clear()
                bird_move = 0.0
                bird_rect.center = (50, DISPLAY_HEIGHT // 2)
                score = 0
                obstacle_number = 0
                pipe_speed = 3

        if event.type == pg.KEYUP:
            if event.key == pg.K_UP or event.key == pg.K_w or event.key == pg.K_DOWN or event.key == pg.K_s:
                bird_move = 0.0
                bird_rotate = 0

        if event.type == bird_flap:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird, bird_rect = animation()

        if event.type == pipe_spawn:
            pipe_list.extend(create_pipe())
            powerUp_spawn_counter += 1
            if pipe_speed <= 4:
                pipe_speed += 0.1
            elif pipe_speed <= 6:
                pipe_speed += 0.05
            elif pipe_speed <= 8:
                pipe_speed += 0.025
            else:
                pipe_speed += 0.01
            pg.time.set_timer(pipe_spawn, int(6000 / pipe_speed))
            
        if event.type == powerUp_spawn:
            if powerUp_spawn_counter % 15 == 0:	# this adjusts how frequently power-ups will spawn
                powerUp_rect = create_powerUp()
                powerUp_spawn_counter = 0

    display.blit(bg, (0, 0))
    display.blit(bg, (288, 0))
    display.blit(bg, (576, 0))

    if game:
        # BIRD
        bird_rect.centery += float(bird_move)

        display.blit(pg.transform.rotate(bird, bird_rotate), bird_rect)
        game = check_collision(pipe_list)
        check_collision_pu(powerUp_rect)  # checks for collision with power up
        if powerUp_active:
            seconds = (pg.time.get_ticks() - start_ticks) / 1000  # calculate how many seconds
            if seconds > 5:  # if more than 5 seconds, then clear the power up
                # This function sets all the power up effects back to default values
                deactivate_pu()
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

    else:
        deactivate_pu()
        display.blit(bg_game_over, bg_game_over_rect)

        # PIPE
        pipe_list = move_pipe(pipe_list)
        pipe_list = remove_pipe(pipe_list)
        
        # POWER-UP
        powerUp_rect = move_powerUp(powerUp_rect)
        
        # SCORE
        high_score = score_update(score, high_score)
        score_display('game_over')

    # FLOOR
    move_floor()
    for i in range(3):
        if floor_pos_x[i] <= -DISPLAY_WIDTH:
            floor_pos_x[i] = 0
        floor_pos_x[i] -= 1

    pg.display.update()
