import pygame
from copy import deepcopy

class InputManager:
    def __init__(self, joystick_num, points):
        pygame.joystick.init()
        self.joystick_num = joystick_num
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_num > self.joystick_count:
            print("ERROR: Joystick index exceeds joystick count. i.e. no joystick detected")
            exit(1)
        self.joystick = pygame.joystick.Joystick(self.joystick_num)
        self.joystick.init()
        self.joystick_name = self.joystick.get_name()
        self.axis = self.joystick.get_numaxes()
        self.num_buttons = self.joystick.get_numbuttons()
        self.num_hats = self.joystick.get_numhats()
        self.screenwidth, self.screenheight = points.screenwidth, points.screenheight
        self.scaling = points.radius

        # Adding idle axis as a point for nearest neighbour
        self.idle_axis = (self.input_scaling(self.get_controller_state()))

    def get_controller_state(self):
        self.joystick.init()
        state = {"name": self.joystick_name, "input":{}}

        # Get the axis
        state["input"]["num_axis"] = self.axis
        state["input"]["axis"] = {}
        for i in range(self.axis):
            state["input"]["axis"][i] = self.joystick.get_axis(i)

        # Get the buttons
        state["input"]["num_buttons"] = self.num_buttons
        state["input"]["buttons"] = {}
        for i in range(self.num_buttons):
            state["input"]["buttons"][i] = self.joystick.get_button(i)

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        state["input"]["num_hats"] = self.num_hats
        state["input"]["hats"] = {}
        for i in range(self.num_hats):
            state["input"]["hats"][i] = self.joystick.get_hat(i)

        return state

    def input_scaling(self, state):
        # The scaling is because it is in range of [-1, 1].
        # I needed it in pixels to reach the radius edges.
        joy_axis = state["input"]["axis"]
        
        l_x = joy_axis[0] * self.scaling
        l_y = joy_axis[1] * self.scaling
        r_x = joy_axis[3] * self.scaling
        r_y = joy_axis[4] * self.scaling

        # To make it go from center of both hubs.
        l_x += self.screenwidth // 4
        l_y += self.screenheight // 2
        r_x += (self.screenwidth // 4) * 3
        r_y += self.screenheight // 2
        
        # To integer
        l_x, l_y, r_x, r_y = int(l_x), int(l_y), int(r_x), int(r_y)
        
        return l_x, l_y, r_x, r_y
