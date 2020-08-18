import math
import pygame
from pprint import pprint
from scipy import spatial
from copy import deepcopy
import numpy as np

def polygon(sides, radius=1, rotation=0, translation=None):
    one_segment = math.pi * 2 / sides

    points = [(math.sin(one_segment * i + rotation) * radius, 
                math.cos(one_segment * i + rotation) * radius) 
                for i in range(sides)]

    if translation:
        points = [[sum(pair) for pair in zip(point, translation)] for point in points]
        points = [(int(item[0]), int(item[1])) for item in points]
    return points

class DisplayManager:
    def __init__(self, screenwidth, screenheight, overlay_width, overlay_height, options_left, options_right, alt_options_left, alt_options_right, hub_radius):
        self.screenwidth = screenwidth
        self.screenheight = screenheight
        self.overlay_width = overlay_width
        self.overlay_height = overlay_height

        # Set the width and height of the screen [width,height]
        self.screen = pygame.display.set_mode([self.screenwidth, self.screenheight])
        self.screen_rect = self.screen.get_rect()

        # Options for left and side.
        self.options_left = options_left
        self.num_options_left = len(options_left)
        self.options_right = options_right
        self.num_options_right = len(options_right)

        # Alternate options symbols, reuse points thus length
        self.alt_options_left, self.alt_options_right = alt_options_left, alt_options_right

        self.radius = hub_radius

        self.left_polygon_points, self.right_polygon_points = self.get_points()   
        self.popupSurf = pygame.Surface([overlay_width, overlay_height])
        self.basic_font = pygame.font.SysFont("comicsansms", 72)
        
        self.left_text_surfaces, self.right_text_surfaces = [], []
        self.alt_left_text_surfaces, self.alt_right_text_surfaces = [], []
        for opt in self.options_left:
            self.left_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))
        for opt in self.options_right:
            self.right_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))
        for opt in self.alt_options_left:
            self.alt_left_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))
        for opt in self.alt_options_right:
            self.alt_right_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))

        # The actual popup display surface.
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = screenwidth // 2
        self.popupRect.centery = screenheight // 2
        
        self.left_text_rects, self.right_text_rects = [], []
        self.alt_left_text_rects, self.alt_right_text_rects = [], []
        for item in range(len(self.left_text_surfaces)):
            textRect = self.left_text_surfaces[item].get_rect()
            # Set positions for each left text element.
            textRect.centerx = self.left_polygon_points[item][0]
            textRect.centery = self.left_polygon_points[item][1]
            self.left_text_rects.append(textRect)

        for item in range(len(self.right_text_surfaces)):
            textRect = self.right_text_surfaces[item].get_rect()
            # Set positions for each right text element.
            textRect.centerx = self.right_polygon_points[item][0]
            textRect.centery = self.right_polygon_points[item][1]
            self.right_text_rects.append(textRect)

        for item in range(len(self.alt_left_text_surfaces)):
            textRect = self.alt_left_text_surfaces[item].get_rect()
            # Set positions for each left text element.
            textRect.centerx = self.left_polygon_points[item][0]
            textRect.centery = self.left_polygon_points[item][1]
            self.alt_left_text_rects.append(textRect)

        for item in range(len(self.alt_right_text_surfaces)):
            textRect = self.alt_right_text_surfaces[item].get_rect()
            # Set positions for each right text element.
            textRect.centerx = self.right_polygon_points[item][0]
            textRect.centery = self.right_polygon_points[item][1]
            self.alt_right_text_rects.append(textRect)
    
    def get_points(self):
        left_center = self.screenwidth // 4
        right_center = (self.screenwidth // 4) * 3

        left_points = polygon(sides=self.num_options_left, radius=self.radius, translation=[left_center, self.screenheight//2])
        right_points = polygon(sides=self.num_options_right, radius=self.radius, translation=[right_center, self.screenheight//2])

        return left_points, right_points
    
    def draw_popup(self, l_x, l_y, r_x, r_y, alt = False):
        if not alt:
            # Left side
            for item in range(len(self.left_text_surfaces)):
                textSurf = self.left_text_surfaces[item]
                textRect = self.left_text_rects[item]
                self.popupSurf.blit(textSurf, textRect)
            # Right side
            for item in range(len(self.right_text_surfaces)):
                textSurf = self.right_text_surfaces[item]
                textRect = self.right_text_rects[item]
                self.popupSurf.blit(textSurf, textRect)
        else:
            # Left side
            for item in range(len(self.alt_left_text_surfaces)):
                textSurf = self.alt_left_text_surfaces[item]
                textRect = self.alt_left_text_rects[item]
                self.popupSurf.blit(textSurf, textRect)
            # Right side
            for item in range(len(self.alt_right_text_surfaces)):
                textSurf = self.alt_right_text_surfaces[item]
                textRect = self.alt_right_text_rects[item]
                self.popupSurf.blit(textSurf, textRect)

        pygame.draw.circle(self.popupSurf, (255,0,0), (l_x, l_y), 5, 0)
        pygame.draw.circle(self.popupSurf, (255,0,0), (r_x, r_y), 5, 0)

        self.screen.blit(self.popupSurf, self.popupRect)
        
        # Remove drawn circles.
        self.popupSurf.fill([0,0,0])
        
        pygame.display.update()

    def draw_cursors(self, l_x, l_y, r_x, r_y):
        pygame.draw.circle()

    def get_option(self, l_x, l_y, r_x, r_y, alt = False):
        # This will return the first option, so left stick takes precedence
        if not alt:
            for item in range(len(self.left_text_rects)):
                if self.left_text_rects[item].collidepoint(l_x, l_y):
                    return self.options_left[item]
            for item in range(len(self.right_text_rects)):
                if self.right_text_rects[item].collidepoint(r_x, r_y):
                    return self.options_right[item]
        else:
            for item in range(len(self.alt_left_text_rects)):
                if self.alt_left_text_rects[item].collidepoint(l_x, l_y):
                    return self.alt_options_left[item]
            for item in range(len(self.alt_right_text_rects)):
                if self.alt_right_text_rects[item].collidepoint(r_x, r_y):
                    return self.alt_options_right[item]

class InputManager:
    def __init__(self, joystick_num, screenwidth, screenheight, stick_radi, left_points, right_points, left_letters, right_letters, alt_left_letters, alt_right_letters):
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
        self.screenwidth, self.screenheight = screenwidth, screenheight
        self.scaling = stick_radi
        self.idle_axis = (self.input_scaling(self.get_controller_state()))
        self.left_points, self.right_points = deepcopy(left_points), deepcopy(right_points)
        self.left_points.append((self.idle_axis[0], self.idle_axis[1]))
        self.right_points.append((self.idle_axis[2], self.idle_axis[3]))
        self.left_answer, self.right_answer = deepcopy(left_letters)+["IDLE"], deepcopy(right_letters)+["IDLE"]
        self.alt_left_answer, self.alt_right_answer = deepcopy(alt_left_letters)+["IDLE"], deepcopy(alt_right_letters)+["IDLE"]

    def get_controller_state(self):
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

    def get_closest_point(self, l_x, l_y, r_x, r_y, not_alt):
        # If closest to idle, ignore.
        l_distance,l_index = spatial.KDTree(self.left_points).query([(l_x, l_y)])
        r_distance,r_index = spatial.KDTree(self.right_points).query([(r_x, r_y)])

        if not_alt:
            return {"left": self.left_answer[l_index[0]], "right": self.right_answer[r_index[0]]}
        else:
            return {"left": self.alt_left_answer[l_index[0]], "right": self.alt_right_answer[r_index[0]]}


if __name__ == "__main__":
    pygame.init()
    left_letters = list("abcdefgh")
    right_letters = list("ijklmnop")
    alt_left_letters = list("qrstuvwx")
    alt_right_letters = list("yz.,_-?;")
    left_letters = list(left_letters)
    right_letters = list(right_letters)
    width, height = 1024, 576
    display = DisplayManager(screenwidth=width, screenheight=height, 
                            overlay_width=width, overlay_height=height, 
                            options_left=left_letters, options_right=right_letters,
                            alt_options_left=alt_left_letters, alt_options_right=alt_right_letters,
                            hub_radius=200)

    input = InputManager(0, screenwidth=width, screenheight=height, stick_radi=display.radius,
                        left_points=display.left_polygon_points, right_points=display.right_polygon_points,
                        left_letters=left_letters, right_letters=right_letters,
                        alt_left_letters=alt_left_letters, alt_right_letters=alt_right_letters)

    # Initialize the joysticks
    done = False
    first = True

    # Used to manage how fast it updates
    clock = pygame.time.Clock()
    FPS = 60
    
    # In milliseconds:
    second_in_ms = 1000
    time_slot_by_fps = 1000 // FPS
    time_tracked_ms = 0
    # Click every 250ms over option.
    time_to_track_ms = 250
    # This is out of a second in ms, i.e. 1000 slots.
    slot_count = 0
    for i in range(second_in_ms):
        if time_tracked_ms < time_to_track_ms:
            time_tracked_ms += time_slot_by_fps
            slot_count += 1

    l_opt_buf = [0 for i in range(slot_count)]
    r_opt_buf = [0 for i in range(slot_count)]
    l_last_opt, r_last_opt = None, None
    count = 0

    # Pressed down state for each key.
    l_state, r_state, alt_l_state, alt_r_state = [], [], [], []
    l_range = len(left_letters+["IDLE"])
    for i in range(l_range):
        if i == l_range:
            l_state.append(True)
        else:
            l_state.append(False)
    for i in range(l_range):
        alt_l_state.append(False)

    r_range = len(right_letters+["IDLE"])
    for i in range(r_range):
        if i == r_range:
            r_state.append(True)
        else:
            r_state.append(False)
    for i in range(r_range):
        alt_r_state.append(False)

    l_answers = left_letters+["IDLE"]
    r_answers = right_letters+["IDLE"]
    alt_l_answers = alt_left_letters+["IDLE"]
    alt_r_answers = alt_right_letters+["IDLE"]

    # Since the lists are the same size, this doesn't matter for both separately:
    l_last_key_pressed, r_last_key_pressed = l_answers.index("IDLE"), r_answers.index("IDLE")
    last_space_key = None
    while done != True:
        state = input.get_controller_state()
        not_alt = state["input"]["buttons"][4] == 0
        #print(state)
        l_x, l_y, r_x, r_y = input.input_scaling(state)
        closest_points = input.get_closest_point(l_x, l_y, r_x, r_y, not_alt=not_alt)

        # Show output        
        #print("l_x: ", l_x, " - l_y: ", l_y, "r_x: ", r_x, " - r_y: ", r_y)
        #print(closest_points)

        # Keeping track of what the closest point was for the last "time_to_track_ms" per ms.
        l_opt_buf[count] = closest_points["left"]
        r_opt_buf[count] = closest_points["right"]

        if not_alt:
            l_key_pressed = l_answers.index(l_opt_buf[count])
            # If there is only one option
            if len(set(l_opt_buf)) == 1:
                if l_key_pressed != l_last_key_pressed:
                    l_state[l_last_key_pressed] = False
                    l_state[l_key_pressed] = True

                    # Suppress "IDLE"
                    if l_key_pressed != l_answers.index("IDLE"):
                        print(l_answers[l_key_pressed], flush=True, end='')

                    #print(l_answers[l_key_pressed])
                    l_last_key_pressed = l_key_pressed

        else:
            l_key_pressed = alt_l_answers.index(l_opt_buf[count])
            # If there is only one option
            if len(set(l_opt_buf)) == 1:
                if l_key_pressed != l_last_key_pressed:
                    alt_l_state[l_last_key_pressed] = False
                    alt_l_state[l_key_pressed] = True

                    # Suppress "IDLE"
                    if l_key_pressed != alt_l_answers.index("IDLE"):
                        print(alt_l_answers[l_key_pressed], flush=True, end='')

                    #print(l_answers[l_key_pressed])
                    l_last_key_pressed = l_key_pressed

        if not_alt:
            r_key_pressed = r_answers.index(r_opt_buf[count])
            # If there is only one option
            if len(set(r_opt_buf)) == 1:
                if r_key_pressed != r_last_key_pressed:
                    r_state[r_last_key_pressed] = False
                    r_state[r_key_pressed] = True
                    
                    # Suppress "IDLE"
                    if r_key_pressed != r_answers.index("IDLE"):
                        print(r_answers[r_key_pressed], flush=True, end='')
                    
                    #print(r_answers[r_key_pressed])
                    r_last_key_pressed = r_key_pressed
        
        else:
            r_key_pressed = alt_r_answers.index(r_opt_buf[count])
            # If there is only one option
            if len(set(r_opt_buf)) == 1:
                if r_key_pressed != r_last_key_pressed:
                    alt_r_state[r_last_key_pressed] = False
                    alt_r_state[r_key_pressed] = True
                    
                    # Suppress "IDLE"
                    if r_key_pressed != alt_r_answers.index("IDLE"):
                        print(alt_r_answers[r_key_pressed], flush=True, end='')
                    
                    #print(r_answers[r_key_pressed])
                    r_last_key_pressed = r_key_pressed

        space_key = state["input"]["buttons"][0] == True | False
        if space_key != last_space_key:
            last_space_key = space_key
            print(" ", flush=True, end='')

        #print("LAST OPTIONS: ", l_last_opt, r_last_opt)

        """
        # Checking if only one option was within those "time_to_track_ms" per ms
        r_set = list(set(r_opt_buf))
        if r_set != {"IDLE"} and r_set != r_last_opt:
            r_last_opt = r_set
            print("PRINT - ", r_opt_buf[0])
        """

        # Wrap around for buffer.
        # -1 for index in range
        if count == (slot_count - 1):
            count = 0
        else: 
            count += 1


        #pprint(state)
        if not_alt:
            display.draw_popup(l_x, l_y, r_x, r_y)
        else:
            display.draw_popup(l_x, l_y, r_x, r_y, alt = True)
        # EVENT PROCESSING STEP
        # User did something
        for event in pygame.event.get():
            # If user clicked close
            if event.type == pygame.QUIT: 
                done = True
            
            """
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")
            if event.type == pygame.JOYAXISMOTION:
                # THE CURRENT PROBLEM IS THAT IT ONLY REGISTERS IF THE JOYSTICK IS MOVING, 
                # IF STILL, IT DOESN'T DO ANYTHING
                exec("")
                #print("Joystick moved.")
            """

        # This isn't actually necessary when I have the Input checking closest points.
        """
        OPTION = display.get_option(l_x, l_y, r_x, r_y)
        if OPTION != None:
            print("OPTION: ", OPTION)
        else:
            print("OPTION: ", "NOTHING")
        """
        # Limit to N frames per second
        clock.tick(FPS)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()