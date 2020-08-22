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
    alt_right_letters = list("yz.,_-?")+["F12"]

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
    display = DisplayManager(points=points, no_frame=False)

    done = False

    # Used to manage how fast it updates
    clock = pygame.time.Clock()

    # Since the lists are the same size, this doesn't matter for both separately:
    last_space_key = None
    while done != True:
        # Get controller data
        state = input.get_controller_state()

        variant = abs(int(state["input"]["axis"][5])) == 0
        upper = abs(int(state["input"]["axis"][2])) == 0
        # It's a bit odd in the initial state.
        if variant:
            variant = 1
        else:
            variant = 0
        # It's a bit odd in the initial state.
        if upper:
            upper = 1
        else:
            upper = 0

        # Update cursor for popup and draw.
        l_x, l_y, r_x, r_y = input.input_scaling(state)
        points.update_cursor(l_x, l_y, r_x, r_y)
        display.draw_popup(variant=variant, upper=upper)

        # Get and execute thumbstick options.
        thumb_option = points.update(variant=variant, upper=upper)
        if thumb_option != None:
            print(thumb_option, flush=True, end='')
            pag.press(str(thumb_option))

        # Structure for keys pressed.
        keys = []
        
        # The "X" key
        key_pressed = state["input"]["buttons"][0] == 1
        keys.append({"key": key_pressed, "value": " ", "needed_time": 20, "repeat_time": 10, "python_print_value": " "})
        # The "B" key
        key_pressed = state["input"]["buttons"][1] == 1
        keys.append({"key": key_pressed, "value": "\b", "needed_time": 20, "repeat_time": 50, "python_print_value": "\b \b"})

        # Execute all keys in list
        for key in keys:
            res = points.buffer_key(key=key["key"], value=key["value"], upper=upper, needed_time_ms=key["needed_time"], repeated_time_ms=key["repeat_time"])
            if res != None:
                print(key["python_print_value"], flush=True, end="")
                pag.press(str(key["value"]))

        # This is necessary for input from controller.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Limit to N frames per second and update time for input
        clock.tick(FPS)
        points.update_time(clock.get_time())

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()