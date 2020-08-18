import math
import pygame
from pprint import pprint
from scipy import spatial
import numpy as np

def polygon(sides, radius=1, rotation=0, translation=None):
    one_segment = math.pi * 2 / sides

    points = [(math.sin(one_segment * i + rotation) * radius, 
                math.cos(one_segment * i + rotation) * radius) 
                for i in range(sides)]

    if translation:
        points = [[sum(pair) for pair in zip(point, translation)] for point in points]

    return points

class DisplayManager:
    def __init__(self, screenwidth, screenheight, overlay_width, overlay_height, options_left, options_right, hub_radius):
        pygame.init()
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
        self.radius = hub_radius

        self.left_polygon_points, self.right_polygon_points = self.get_points()   
        self.popupSurf = pygame.Surface([overlay_width, overlay_height])
        self.basic_font = pygame.font.SysFont("comicsansms", 72)
        
        self.left_text_surfaces, self.right_text_surfaces = [], []
        for opt in self.options_left:
            self.left_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))
        for opt in self.options_right:
            self.right_text_surfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))

        # The actual popup display surface.
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = screenwidth // 2
        self.popupRect.centery = screenheight // 2
        
        self.left_text_rects, self.right_text_rects = [], []
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
    
    def get_points(self):
        left_center = self.screenwidth // 4
        right_center = (self.screenwidth // 4) * 3

        left_points = polygon(sides=self.num_options_left, radius=self.radius, translation=[left_center, self.screenheight//2])
        right_points = polygon(sides=self.num_options_right, radius=self.radius, translation=[right_center, self.screenheight//2])

        return left_points, right_points
    
    def draw_popup(self, l_x, l_y, r_x, r_y):
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
        pygame.draw.circle(self.popupSurf, (255,0,0), (l_x, l_y), 5, 0)
        pygame.draw.circle(self.popupSurf, (255,0,0), (r_x, r_y), 5, 0)

        self.screen.blit(self.popupSurf, self.popupRect)
        
        # Remove drawn circles.
        self.popupSurf.fill([0,0,0])
        
        pygame.display.update()

    def draw_cursors(self, l_x, l_y, r_x, r_y):
        pygame.draw.circle()

    def get_option(self, l_x, l_y, r_x, r_y):
        # This will return the first option, so left stick takes precedence
        for item in range(len(self.left_text_rects)):
            if self.left_text_rects[item].collidepoint(l_x, l_y):
                return self.options_left[item]
        for item in range(len(self.right_text_rects)):
            if self.right_text_rects[item].collidepoint(r_x, r_y):
                return self.options_right[item]

def get_controller_state(): 
    state = {}
   
    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    state["joystick_count"] = joystick_count
    state["joysticks"] = {}    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        
        # Get the name from the OS for the controller/joystick
        state["joysticks"][i] = {"name": joystick.get_name()}
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        state["joysticks"][i]["num_axies"] = axes
        
        state["joysticks"][i]["joystick_axis"] = {}
        for j in range(axes):
            axis = joystick.get_axis(j)
            state["joysticks"][i]["joystick_axis"][j] = axis

        buttons = joystick.get_numbuttons()
        state["joysticks"][i]["num_buttons"] = buttons

        state["joysticks"][i]["buttons"] = {}
        for j in range(buttons):
            button = joystick.get_button(j)
            state["joysticks"][i]["buttons"][j] = button
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        state["joysticks"][i]["num_hats"] = hats

        state["joysticks"][i]["hats"] = {}
        for j in range(hats):
            hat = joystick.get_hat(j)
            state["joysticks"][i]["hats"][j] = hat
        
    return state

if __name__ == "__main__":
    left_letters = "1234567"
    right_letters = "abcdefg"
    left_letters = list(left_letters)
    right_letters = list(right_letters)
    width, height = 1024, 576
    display = DisplayManager(screenwidth=width, screenheight=height, 
                            overlay_width=width, overlay_height=height, 
                            options_left=left_letters, options_right=right_letters,
                            hub_radius=200)

    # Initialize the joysticks
    pygame.joystick.init()
    done = False
    first = True

    # Used to manage how fast it updates
    clock = pygame.time.Clock()
    FPS = 60

    while done != True:
        state = get_controller_state()

        # The 200 is because it is in pixels, scaling factor
        joy_axis = state["joysticks"][0]["joystick_axis"]
        
        pix_move_scaling = display.radius
        l_x = joy_axis[0] * pix_move_scaling
        l_y = joy_axis[1] * pix_move_scaling
        r_x = joy_axis[3] * pix_move_scaling
        r_y = joy_axis[4] * pix_move_scaling

        # To make it go from respective radial interface center
        l_x += display.screenwidth//4
        l_y += display.screenheight//2
        r_x += (display.screenwidth//4) * 3
        r_y += display.screenheight//2

        # Get idles for closest detection.
        if first:
            l_x_idle, l_y_idle = l_x, l_y
            r_x_idle, r_y_idle = r_x, r_y
            left_to_query = display.left_polygon_points
            left_to_query.append((l_x_idle, l_y_idle))
            right_to_query = display.right_polygon_points
            right_to_query.append((r_x_idle, r_y_idle))
            left_answer = left_letters + ["IDLE"]
            right_answer = right_letters + ["IDLE"]
            first = False

        # If closest to idle, ignore.
        l_distance,l_index = spatial.KDTree(left_to_query).query([(l_x, l_y)])
        r_distance,r_index = spatial.KDTree(right_to_query).query([(r_x, r_y)])

        print("Closest Points: ", "L_STICK - ", left_answer[l_index[0]], ", R_STICK - ", right_answer[r_index[0]])

        # Change all to int.
        l_x, l_y, r_x, r_y = int(l_x), int(l_y), int(r_x), int(r_y)
        
        print("l_x: ", l_x, " - l_y: ", l_y, "r_x: ", r_x, " - r_y: ", r_y)

        #pprint(state)
        display.draw_popup(l_x, l_y, r_x, r_y)

        # EVENT PROCESSING STEP
        # User did something
        for event in pygame.event.get():
            # If user clicked close
            if event.type == pygame.QUIT: 
                done = True

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



        OPTION = display.get_option(l_x, l_y, r_x, r_y)
        if OPTION != None:
            print("OPTION: ", OPTION)
        else:
            print("OPTION: ", "NOTHING")

        # Limit to N frames per second
        clock.tick(FPS)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()