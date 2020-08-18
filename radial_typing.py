import math
import pygame
from pprint import pprint

def polygon(sides, radius=1, rotation=0, translation=None):
    one_segment = math.pi * 2 / sides

    points = [(math.sin(one_segment * i + rotation) * radius, 
                math.cos(one_segment * i + rotation) * radius) 
                for i in range(sides)]

    if translation:
        points = [[sum(pair) for pair in zip(point, translation)] for point in points]

    return points

class DisplayManager:
    def __init__(self, screenwidth, screenheight, overlay_width, overlay_height, options):
        pygame.init()
        self.screenwidth = screenwidth
        self.screenheight = screenheight
        self.overlay_width = overlay_width
        self.overlay_height = overlay_height

        # Set the width and height of the screen [width,height]
        self.screen = pygame.display.set_mode([self.screenwidth, self.screenheight])
        
        self.screen_rect = self.screen.get_rect()
        self.options = options
        self.num_options = len(options)
        self.polygon_points = self.get_points()   
        self.popupSurf = pygame.Surface([overlay_width, overlay_height])
        self.basic_font = pygame.font.SysFont("comicsansms", 72)
        self.font_linesize = pygame.font.Font.get_linesize(self.basic_font)
        
        self.textSurfaces = []
        for opt in self.options:
            self.textSurfaces.append(self.basic_font.render(opt, 1, (0, 0, 255)))
        
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = screenwidth // 2
        self.popupRect.centery = screenheight // 2
        
        self.textRects = []
        for item in range(len(self.textSurfaces)):
            textRect = self.textSurfaces[item].get_rect()
            """
            textRect.top = self.screen_rect.top
            textRect.left = self.screen_rect.left
            self.screen_rect.top += self.font_linesize
            """
            textRect.centerx = self.polygon_points[item][0]
            textRect.centery = self.polygon_points[item][1]
            self.textRects.append(textRect)
    
    def get_points(self):
        points = polygon(sides=self.num_options, radius=175, translation=[self.screenwidth//2, self.screenheight//2])
        return points
    
    def draw_popup(self):
        for item in range(len(self.textSurfaces)):
            textSurf = self.textSurfaces[item]
            textRect = self.textRects[item]
            self.popupSurf.blit(textSurf, textRect)

        self.screen.blit(self.popupSurf, self.popupRect)
        pygame.display.update()

    def get_option(self, axis_x, axis_y):
        for item in range(len(self.textRects)):
            if self.textRects[item].collidepoint(axis_x, axis_y):
                return self.options[item]

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
    left_stick_letters = "QWERTASDFGZXCV"
    left_stick_letters = list(left_stick_letters)
    display = DisplayManager(screenwidth=1920, screenheight=1080, overlay_width=1920, overlay_height=1080, options=left_stick_letters)
    # Initialize the joysticks
    pygame.joystick.init()
    done = False

    # Used to manage how fast it updates
    clock = pygame.time.Clock()
    FPS = 1

    while done != True:
        state = get_controller_state()
        #pprint(state)
        display.draw_popup()

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
                
                print("Joystick moved.")
                # The 50 is because it is in pixels, scaling factor
                joy_axis = state["joysticks"][0]["joystick_axis"]
                pix_move_scaling = 200
                axis_x = joy_axis[0] * pix_move_scaling
                axis_y = joy_axis[1] * pix_move_scaling

                # To make it go from center of screen.
                axis_x += display.screenwidth//2
                axis_y += display.screenheight//2

                print("axis_x: ", axis_x, " - axis_y: ", axis_y)
                print(display.polygon_points)

                OPTION = display.get_option(axis_x, axis_y)
                if OPTION != None:
                    print(OPTION)

        # Limit to N frames per second
        clock.tick(FPS)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()