import pygame
from pprint import pprint
import pyautogui as pag

from DisplayManager import DisplayManager
from PointsAndOptionManager import PointAndOptionManager
from InputManager import InputManager

if __name__ == "__main__":
    pygame.init()

    FPS = 30

    left_letters = list("abcdefgh")
    right_letters = list("ijklmnop")
    alt_left_letters = list("qrstuvwx")
    alt_right_letters = list("yz.,_-?;")

    options_left = {0: left_letters, 1: alt_left_letters}
    options_right = {0: right_letters, 1: alt_right_letters}

    dimensions = {"screenwidth": 1024, "screenheight": 576, 
                "overlay_width": 1024, "overlay_height": 576}

    # Initialise PointAndOptionManager
    points = PointAndOptionManager(dimensions, options_left, options_right, FPS, hub_radius=150)

    # Initialise InputManager, get idle_axis, update points with idle_axis.
    input = InputManager(joystick_num=0, points=points)
    idle_axis = (input.input_scaling(input.get_controller_state()))
    points.update_idle_points(idle_axis)
    
    # Initialise the display.
    display = DisplayManager(points=points, no_frame=True)

    done = False

    # Used to manage how fast it updates
    clock = pygame.time.Clock()

    # Since the lists are the same size, this doesn't matter for both separately:
    last_space_key = None
    while done != True:
        state = input.get_controller_state()
        variant = abs(state["input"]["axis"][5])
        if variant != 1.0 and variant != 0.0:
            variant = 1
        else:
            variant = 0

        display.draw_popup(variant=variant)
        l_x, l_y, r_x, r_y = input.input_scaling(state)
        points.update_cursor(l_x, l_y, r_x, r_y)
        thumb_option = points.update(variant=variant)

        if thumb_option != None:
            print(thumb_option, flush=True, end='')
            pag.press(str(thumb_option))                                     

        # If key buffered, return space
         # The "X" key
        key_pressed = state["input"]["buttons"][0] == 1
        res = points.buffer_key(key=key_pressed, value=" ", needed_time_ms=20)
        if res != None:
            print(res, flush=True, end='')
            pag.press(str(res))

        # If key buffered, return backspace
         # The "B" key
        key_pressed = state["input"]["buttons"][1] == 1
        res = points.buffer_key(key=key_pressed, value="\b", needed_time_ms=20)
        if res != None:
            # The "end=" part is necessary for the python console.
            print(res, flush=True, end=' \b')
            pag.press(str(res))

        # This is necessary for input from controller.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Limit to N frames per second
        clock.tick(FPS)
        points.update_time(clock.get_time())
        #print(clock.get_time())

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()