import pygame
from pprint import pprint
import pyautogui as pag

from display import DisplayManager
from data import DataManager
from inputs import InputManager

if __name__ == "__main__":
    pygame.init()

    FPS = 30

    # Written strangely to show up better
    left0 = list(r"edcbahgf") 
    right0 = list(r"mlkjipon")
    left1 = list(r"utsrqxwv")
    right1 = list(r"yz") + ["FUC", "NUM", "SYM", "PNC"] 
    left2 = list(r"012345678")
    right2 = list(r"9-+*/^%") + ["BACK"]
    left3 = ["F5", "F4", "F3", "F2", "F1", "F8", "F7", "F6"]
    right3 = ["F12", "F11", "F10", "F9", "BACK"]
    left4 = list(r"<>{}[]()")
    right4 = ["Vol+", "Vol-", "VolMute", "Win", "PrtScr", "BACK"]
    left5 = list(r"!?\"'@#~¬")
    right5 = list(r"`.,&\|") + ["BACK"]

    options = {"left_0": left0, "right_0": right0,
                "left_1": left1, "right_1": right1,
                "left_2": left2, "right_2": right2,
                "left_3": left3, "right_3": right3,
                "left_4": left4, "right_4": right4,
                "left_5": left5, "right_5": right5}

    dimensions = {"screenwidth": 1024, "screenheight": 576, 
                "overlay_width": 1024, "overlay_height": 576}

    # Initialise DataManager
    points = DataManager(dimensions, options, FPS, hub_radius=200)

    # Initialise InputManager, get idle_axis, update points with idle_axis.
    inputs = InputManager(joystick_num=0, points=points, rumble_ms=40)
    points.update_idle_points(inputs.idle_axis)
    
    # Initialise the display.
    display = DisplayManager(points=points, no_frame=False)

    # Used to manage how fast it updates
    clock = pygame.time.Clock()

    # Loop variables.
    done = False
    variant = 0
    wait_time = 220

    while done != True:
        # Get controller data
        state = inputs.get_controller_state()
        # It's a bit odd in the initial state
        mod1 = abs(int(state["input"]["buttons"][5])) == 1
        upper = abs(int(state["input"]["buttons"][4])) == 1

        # The Power Button
        #print(abs(int(state["input"]["buttons"][8])) == 1)

        if variant == 1:
            variant = 0

        if mod1 and variant == 0:
            variant = 1

        if upper:
            upper = True
        else:
            upper = False

        # Update cursor for popup and draw.
        l_x, l_y, r_x, r_y = inputs.input_scaling(state)
        points.update_cursor(l_x, l_y, r_x, r_y)
        display.draw_popup(variant=variant, upper=upper)

        # Structure for keys pressed.
        keys = []

        # Get thumbstick options.
        thumb_option = points.update(variant=variant, upper=upper, wait_time=wait_time)
        if thumb_option == "BACK":
            inputs.rumble()
            variant = 0
        elif thumb_option == "NUM":
            inputs.rumble()
            wait_time = 500
            variant = 2
        elif thumb_option == "FUC":
            inputs.rumble()
            wait_time = 500
            variant = 3
        elif thumb_option == "SYM":
            inputs.rumble()
            wait_time = 500
            variant = 4
        elif thumb_option == "PNC":
            inputs.rumble()
            wait_time = 500
            variant = 5
        elif thumb_option != None:
            inputs.rumble()
            pag.press(thumb_option)
            wait_time = 220

        
        # The "X" key
        key_pressed = state["input"]["buttons"][0] == 1
        keys.append({"key": key_pressed, "value": "space", "time": 20, "repeat": 10})
        # The "B" key
        key_pressed = state["input"]["buttons"][1] == 1
        keys.append({"key": key_pressed, "value": "backspace", "time": 20, "repeat": 50})
        # The "Y" key
        key_pressed = state["input"]["buttons"][3] == 1
        keys.append({"key": key_pressed, "value": "enter", "time": 20, "repeat": 50})
        # D-Pad (Left)
        key_pressed = state["input"]["hats"][0] == (-1, 0)
        keys.append({"key": key_pressed, "value": "home", "time": 20, "repeat": 50})
        # D-Pad (Right)
        key_pressed = state["input"]["hats"][0] == (1, 0)
        keys.append({"key": key_pressed, "value": "end", "time": 20, "repeat": 50})
        # D-Pad (Down)
        key_pressed = state["input"]["hats"][0] == (0, -1)
        keys.append({"key": key_pressed, "value": "pgdn", "time": 20, "repeat": 50})
        # D-Pad (Up)
        key_pressed = state["input"]["hats"][0] == (0, 1)
        keys.append({"key": key_pressed, "value": "pgup", "time": 20, "repeat": 50})

        # Execute all keys in list
        for key in keys:
            res = points.buffer_key(key=key["key"], value=key["value"], 
                                    upper=upper, needed_time_ms=key["time"], 
                                    repeated_time_ms=key["repeat"])
            if res != None:
                pag.press(key["value"])

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