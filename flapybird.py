import pygame as pg
import time
from sys import exit
from random import choice
from FlaPyBird.constants import *	# holds some important constant values 


def animation():			# function to animate the bird flapping and power-up graphics 
    new_powerUp2 = powerUp2_frames[powerUp2_index]		# cycle power-up graphics 
    new_powerUp2_rect = new_powerUp2.get_rect(center=(powerUp_rect.centerx, powerUp_rect.centery))
    
    global speedy_active		# check if bird is "speedy" (lightning power-up)
    if speedy_active == False:		# if not:
        new_bird = bird_frames[bird_index]		# cycle normal (blue) bird animation frames 
        new_bird_rect = new_bird.get_rect(center=(50, bird_rect.centery))
    if speedy_active == True:			# if so:
        new_bird = bird_speedy_frames[bird_index]	# cycle speedy (yellow) bird animation frames 
        new_bird_rect = new_bird.get_rect(center=(50, bird_rect.centery))

    return new_bird, new_bird_rect, new_powerUp2, new_powerUp2_rect		# return updated bird and PU values 


def create_pipe():			# function to create pipes in randomly-chosen positions
    random_pipe = choice(pipe_hei)
    top_pipe = pipe.get_rect(midbottom=(DISPLAY_WIDTH + 26, random_pipe - 150))
    bottom_pipe = pipe.get_rect(midtop=(DISPLAY_WIDTH + 26, random_pipe))

    return top_pipe, bottom_pipe	# returns the objects for the top and bottom pipes created


def draw_pipe(pipes):			# function to visually display all active pipes 
    for p in pipes:				# iterates through list of pipes
        if p.bottom >= DISPLAY_HEIGHT:	# ensure pipes are within display region
            display.blit(pipe, p)			#display normally if so
        else:					# if not: 
            flip_pipe = pg.transform.flip(pipe, False, True)	# flip the pipes so that they fit in the correct space 
            display.blit(flip_pipe, p)		# display corrected pipes 


def move_pipe(pipes):		# function to move pipes
    for p in pipes:			# iterates through pipes in list
        p.centerx -= pipe_speed	# and adjusts their X-position according to the pipe movement speed 

    return pipes		# return the list of pipes with updated positional values 


def spawn_pipe():			# function that manages creating new pipes at the correct time
    if event.type == pipe_spawn:
        pipe_list.append(create_pipe())	# append new pipes to pipe list 


def remove_pipe(pipes):		# function to remove pipes when they go off-screen
    global obstacle_number

    if len(pipes) != 0:		# if pipe list is not empty:
        if pipes[0][0] + 52 <= 0:		# if oldest pipe is off the screen:
            pipes.pop(0)			# pop pipes from list
            pipes.pop(0)			# (both top and bottom pipes)
            obstacle_number -= 2	# decrease number of extant obstacles 
    
    return pipes[:]		# return updated pipe list 


def move_floor():		# function to move mosition of floor and display it 
    for i in range(3):			# floor is tiled across three times: do the following for each tile: 
        display.blit(floors[i], (floor_pos_x[i], DISPLAY_HEIGHT - floor_rects[i].height // 2))
        display.blit(floors[i], (floor_pos_x[i] + DISPLAY_WIDTH, DISPLAY_HEIGHT - floor_rects[i].height // 2))


def check_obstacle_passed():		# function to detect when the bird passes through pipes 
    global obstacle_number
    pipes = pipe_list[:]

    if len(pipes) > obstacle_number:			# check number of pipes against obstacle counter
        if pipes[obstacle_number][0] + 52 <= 26:	# if bird has passed a set of pipes (they have despawned):
            obstacle_number += 2
            point_snd.play()			# play ding sound 
            return True		# return true for successful pass

    return False		# otherwise return false 


def check_collision(pipes):		# function to detect when the bird hits pipes 
    for p in pipes:
        if bird_rect.colliderect(p):	# PyGame method to check for collision
            collide_snd.play()	# if collided, play collision sound 
            return False		# return false, bird did not pass pipes 

    for i in range(3):		# if bird hits top of screen or floor:
        if bird_rect.top <= 0 or bird_rect.bottom >= DISPLAY_HEIGHT - floor_rects[i].height // 2:
            collide_snd.play()	# detect as collision
            return False

    return True	# otherwise return true
    
    
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
        display.blit(powerUp1, powerUp_rect_obj)	# animate the movement of the current power-up on screen 
    if currentPU_type == 2:
        display.blit(powerUp2, powerUp_rect_obj)
    if currentPU_type == 3:
        display.blit(powerUp3, powerUp_rect_obj)
                
                
def move_powerUp(powerUp_rect_obj): 	# move the power-ups across the screen 
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
        global speedy_active		# activate global boolean indicating that bird is "speedy" 
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
    

def score_display(game_state):	# function to display scores and indicators, as well as game-over 
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


def display_active_power_ups(p_ups_active):	# displays the currently-active power-up type 
    if p_ups_active[0]:
        pu_rect = powerUp1.get_rect(center=(DISPLAY_WIDTH // 2 - 225, 50))
        display.blit(powerUp1, pu_rect)
    if p_ups_active[1]:
        pu_rect = powerUp2.get_rect(center=(DISPLAY_WIDTH // 2 - 150, 50))
        display.blit(powerUp2, pu_rect)
    if p_ups_active[2]:
        pu_rect = powerUp3.get_rect(center=(DISPLAY_WIDTH // 2 - 75, 50))
        display.blit(powerUp3, pu_rect)


def increment_score(scr, increment):	# inscrement score if obstacle is successfully passed 
    if check_obstacle_passed():
        return scr + increment

    return scr


def score_update(scr, high_scr, pu_scr, pu_high_scr):	# function to update the high-score displayed 
    if scr > high_scr:
        high_scr = scr
    if pu_scr > pu_high_scr:
        pu_high_scr = pu_scr

    return high_scr, pu_high_scr


# initialization and blogabl variables
'DISPLAY'
display = pg.display.set_mode(DISPLAY_AREA)
pg.display.set_caption('FlaPyBird')

'BACKGROUND'
bg = pg.image.load('assets/images/sprites/Background.png').convert()
floors = []				# container for floor objects (for display)
floor_pos_x = [0, 288, 576]		# tiling positions of floors
floor_rects = []			# floor PyGame rect object array 
for i in range(3):
    floors.append(pg.image.load('assets/images/sprites/Floor.png').convert_alpha())
    floor_rects.append(floors[i].get_rect())

pipe = pg.image.load('assets/images/sprites/Pipe.png')
pipe_list = []			# list of active pipes 
pipe_spawn = pg.USEREVENT	# put pipe-spawn in the PyGame event queue 
obstacle_number = 0		# number of obstacles 

pipe_speed = 3			# speed at which pipes move
pipe_speed_store = 3		# stores current pipe speed for use when slow-down power-up activates 
pipe_spacing = 6000		# value to determine how far apart the pipes will spawn
pg.time.set_timer(pipe_spawn, int(pipe_spacing / pipe_speed))	# delay between spawning another pipe 
pipe_hei = [200, 300, 400]		# list of heights pipes can spawn at, for randomization 
bg_game_over = pg.image.load('assets/images/sprites/Game_Over.png')
bg_game_over_rect = bg_game_over.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 25))

'BIRD'
bird_down = pg.image.load('assets/images/sprites/Bird_down.png').convert_alpha()
bird_mid = pg.image.load('assets/images/sprites/Bird_mid.png').convert_alpha()
bird_up = pg.image.load('assets/images/sprites/Bird_up.png').convert_alpha()
bird_frames = [bird_down, bird_mid, bird_up]		# list of bird animation frames 

bird_down_speedy = pg.image.load('assets/images/sprites/Bird_down_speedy.png').convert_alpha()
bird_mid_speedy = pg.image.load('assets/images/sprites/Bird_mid_speedy.png').convert_alpha()
bird_up_speedy = pg.image.load('assets/images/sprites/Bird_up_speedy.png').convert_alpha()
bird_speedy_frames = [bird_down_speedy, bird_mid_speedy, bird_up_speedy]	# speedy frames 

bird_index = 0		# animation frame index 
bird = bird_frames[bird_index]	# bird object, uses a frame from the animation list 
bird_rect = bird.get_rect(center=(50, DISPLAY_HEIGHT // 2))

speedy_active = False		# global variable, boolean for whether bird is currently speedy (lightning PU)
bird_speedy = bird_speedy_frames[bird_index]	# speedy bird (a different color) 
bird_speedy_rect = bird_speedy.get_rect(center=(50, DISPLAY_HEIGHT // 2))

bird_flap = pg.USEREVENT + 1		# add bird-flapping (animation) to PyGame event queue
pg.time.set_timer(bird_flap, 200)	# delay between bird animation frames 
bird_move = 0.0			# global variable for bird movement 
bird_rotate = 0			# global variable for bird tilt
bird_moving_up = False			# boolean for moving upward check
bird_moving_down = False		# boolean for moving downward check

'POWER-UP'
powerUp1 = pg.image.load('assets/images/sprites/lightning.png').convert_alpha() 	# PU1, "speed"
powerUp2_frames = [pg.image.load('assets/images/sprites/R_Pickup_1.png.png').convert_alpha(),	# PU2, "space"
                   pg.image.load('assets/images/sprites/R_Pickup_2.png.png').convert_alpha(),
                   pg.image.load('assets/images/sprites/R_Pickup_3.png.png').convert_alpha()]
powerUp3 = pg.image.load('assets/images/sprites/clock_icon.png').convert_alpha()	# PU3, "slow"
powerUp2 = powerUp2_frames[0]		# initialize PU2 animation starting frame 
powerUp2_index = 0			# index for PU animation (PU2 flashes) 
powerUp_types = [1, 2, 3]		# list of PU types. for randomization. 
currentPU_type = 1		# default to 1, changed when new ones spawned 
powerUp_duration = 5		# default to 5, can be adjusted if desired 

powerUp_spawn = pg.USEREVENT		# Put Power-Up spawn in PyGame event queue 
powerUp_spawn_counter = 0	# counter used to determine when to spawn a power-up
powerUp_height = [-100, 0, 100]	# list of heights at which a PU can spawn 
powerUp_rect = powerUp1.get_rect(center=(DISPLAY_WIDTH + 20, DISPLAY_HEIGHT // 2))
powerUp_active = False  	# global boolean for if there is a power-up active 
p_ups_active = [False, False, False]		# list of currently-active power-ups 
start_ticks = 0  # start_ticks starts the timer for the power up
speed_multiplier = 1.0		# speed multiplier for "speed" power-up

'SOUND EFFECTS'				# initialize sound effects 
pg.mixer.init(44100, 16, 2, 512)
flap_snd = pg.mixer.Sound('assets/sounds/sound_effects/Flap.ogg')
collide_snd = pg.mixer.Sound('assets/sounds/sound_effects/Hit.ogg')
point_snd = pg.mixer.Sound('assets/sounds/sound_effects/Point.ogg')

'FONT'				# initialize fonts 
pg.font.init()
font = pg.font.Font('assets/font/04B_19.ttf', 20)

'SCORE'		# initialize score, PU-score, and hich-score values 
high_score = 0
score = high_score
pu_score = 0
pu_high_score = pu_score

'FPS'				# initialize framerate and clock speed 
clock = pg.time.Clock()
fps = 60

'LOOP'				# main game loop
game = True
while True:				# while the game is not in game-over status:
    clock.tick(fps)			# limit clock rate to the specified fps value

    for event in pg.event.get():		# for each event in the PyGame event queue:
        if event.type == pg.QUIT:
            pg.quit()				# quit PyGame if game is exited
            exit()

        if event.type == pg.KEYDOWN:			# if a key is pressed:
            if event.key == pg.K_UP or event.key == pg.K_w:		# if move-up:
                bird_moving_up = True					# set moving status to true
            if event.key == pg.K_DOWN or event.key == pg.K_s:	# same for move-down
                bird_moving_down = True
            if event.key == pg.K_SPACE and not game:		# if in game-over status and SPACE is pressed:
                game = True					# start game again		
                pipe_list.clear()			#clear any pipes from screen before starting 
                bird_move = 0.0			# reset bird movement
                bird_rect.center = (50, DISPLAY_HEIGHT // 2)		# reset bird position
                score = 0				# reset score
                pu_score = 0				# and power-up counter
                obstacle_number = 0			# clear obstacle list 
                pipe_speed = 3			# reset speed of pipes to starting value 

        if event.type == pg.KEYUP:			# if a key is released:
            if event.key == pg.K_UP or event.key == pg.K_w:		# if key was a movement key:
                bird_moving_up = False				#halt bird movement
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                bird_moving_down = False

        if event.type == bird_flap: 		# when the bird flaps (animation update):
            if bird_index < 2:		# cycle through animation frames
                bird_index += 1
            else:
                bird_index = 0

            if powerUp2_index < 2:		# power-up animation works on the same timer
                powerUp2_index += 1
            else:
                powerUp2_index = 0

            bird, bird_rect, powerUp2, powerUp_rect = animation()	# call the animation function to update visuals


        if event.type == pipe_spawn:			# when a pipe spawns:
            pipe_list.extend(create_pipe())		# add it to the list of pipes 
            powerUp_spawn_counter += 1		# add to counter that controls frequency of Power-Up spawns
            if pipe_speed <= 4:		# this segment progressively increases the speed of the pipes
                pipe_speed += 0.125
            elif pipe_speed <= 6:		# at certain intervals, the acceleration changes
                pipe_speed += 0.1
            elif pipe_speed <= 8:
                pipe_speed += 0.075
            else:
                pipe_speed += 0.05		#final slow-but-constant speed increase 
            pg.time.set_timer(pipe_spawn, int(pipe_spacing / pipe_speed))	# controls delay between pipe spawns 
            
        if event.type == powerUp_spawn:		# If a Power-Up spawn is called:
            if powerUp_spawn_counter % 5 == 0:	# check if it is time to spawn another Power-Up
                random_pu_type = choice(powerUp_types)		# if so, pick a random type
                powerUp_rect = create_powerUp(random_pu_type)	# and create the PyGame object for it 
                powerUp_spawn_counter = 0				# and reset the counter for spawning another

    # Bird movement
    if bird_moving_up and bird_moving_down:		# if both movement directions are active, cancel movement 
        bird_move = 0.0
        bird_rotate = 0
    elif bird_moving_up:				# logic to move and tilt the bird up
        bird_move = -4.0 * speed_multiplier
        bird_rotate = 20
    elif bird_moving_down:				# logic to move and tilt the bird down
        bird_move = 4.0 * speed_multiplier
        bird_rotate = -20
    else:						# default: no movement 
        bird_move = 0.0
        bird_rotate = 0

    display.blit(bg, (0, 0))		# display the background (graphic is tiled three times horizontally) 
    display.blit(bg, (288, 0))
    display.blit(bg, (576, 0))

    if game:						# if game is active (not game-over): 
        # BIRD
        bird_rect.centery += float(bird_move)		# adjust the bird positional value according to movement 

        display.blit(pg.transform.rotate(bird, bird_rotate), bird_rect)	# display bird rotation
        game = check_collision(pipe_list)					#check for collision with pipe 
        pu_score += check_collision_pu(powerUp_rect, p_ups_active)  # check for collision with power-up
        if powerUp_active:			# if bird touched power-up: 
            seconds = (pg.time.get_ticks() - start_ticks) / 1000  # calculate how many seconds (duration)
            if seconds > powerUp_duration:  # if more than 5 seconds, then clear the power up
                # This function sets all the power up effects back to default values:
                deactivate_pu(currentPU_type, p_ups_active)
                powerUp_active = False

        # PIPE
        draw_pipe(pipe_list)				# display all active pipes 
        pipe_list = move_pipe(pipe_list)		# and move them
        pipe_list = remove_pipe(pipe_list)		# and remove any that go off-screen
        
        # POWER-UP
        draw_powerUp(powerUp_rect)			# display power-ups
        powerUp_rect = move_powerUp(powerUp_rect)	# and move them

        # SCORE
        score_display('main_game')			# display score
        score = increment_score(score, 1)		# increment when appropriate 

        # ACTIVE POWER-UPS
        display_active_power_ups(p_ups_active)	# display the type of any active power-up

    else:							# if the game is not active (is game-over):
        deactivate_pu(currentPU_type, p_ups_active)		# deactivate any power-ups 
        display.blit(bg_game_over, bg_game_over_rect)	# display game-over graphic

        # PIPE						# continue pipe logic, without displaying 
        pipe_list = move_pipe(pipe_list)
        pipe_list = remove_pipe(pipe_list)
        
        # POWER-UP					# same with power-ups 
        powerUp_rect = move_powerUp(powerUp_rect)
        
        # SCORE				# update high-score if relevant 
        high_score, pu_high_score = score_update(score, high_score, pu_score, pu_high_score)
        score_display('game_over')

    # FLOOR				# always animate floor movement:
    move_floor()
    for i in range(3):
        if floor_pos_x[i] <= -DISPLAY_WIDTH:
            floor_pos_x[i] = 0
        floor_pos_x[i] -= 1

    pg.display.update()		# always update the PyGame display window 
