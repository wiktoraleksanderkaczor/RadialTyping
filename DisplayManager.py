import pygame

def toupper(values):
    ret_val = []
    for item in range(len(values)):
        ret_val.append(values[item].upper())
    return ret_val

class DisplayManager:
    def __init__(self, points, no_frame=False):
        # Save point reference
        self.points = points

        # Set the width and height of the screen [width,height]
        if no_frame:
            self.screen = pygame.display.set_mode([points.screenwidth, points.screenheight], pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode([points.screenwidth, points.screenheight])
        self.screen_rect = self.screen.get_rect()

        self.popupSurf = pygame.Surface([points.overlay_width, points.overlay_height])
        basic_font = pygame.font.SysFont("comicsansms", 72)

        # Text surfaces
        self.lower_text_surfaces = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}
        self.upper_text_surfaces = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}

        options = points.options
        # The True and False is for imaginary "is_upper"
        self.text_surfaces = {True: {}, False: {}}
        for key in options.keys():
            self.text_surfaces[True][key] = []
            self.text_surfaces[False][key] = []

        render = basic_font.render
        for key in options.keys():
            for opt in options[key]:
                self.text_surfaces[False][key].append(render(opt, 1, (0, 0, 255)))
            for opt in toupper(options[key]):
                self.text_surfaces[True][key].append(render(opt, 1, (0, 0, 255)))

        # The actual popup display surface.
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = points.screenwidth // 2
        self.popupRect.centery = points.screenheight // 2
        
        self.text_rects = {True: {}, False: {}}
        for key in options.keys():
            self.text_rects[True][key] = []
            self.text_rects[False][key] = []

        for is_upper in [True, False]:
            for key in self.text_surfaces[is_upper].keys():
                for index in range(len(self.text_surfaces[is_upper][key])):
                    textRect = self.text_surfaces[is_upper][key][index].get_rect()
                    textRect.centerx = points.points[key][index][0]
                    textRect.centery = points.points[key][index][1]
                    self.text_rects[is_upper][key].append(textRect)

    def draw_popup(self, variant=0, upper=False):
        variant = str(variant)

        for key in self.text_surfaces[upper].keys():
            if key[-1] == variant:
                for item in range(len(self.text_rects[upper][key])):
                    textSurf = self.text_surfaces[upper][key][item]
                    textRect = self.text_rects[upper][key][item]
                    self.popupSurf.blit(textSurf, textRect)

        l_x, l_y, r_x, r_y = self.points.get_cursor()
        pygame.draw.circle(self.popupSurf, (255,0,0), (l_x, l_y), 5, 0)
        pygame.draw.circle(self.popupSurf, (255,0,0), (r_x, r_y), 5, 0)

        self.screen.blit(self.popupSurf, self.popupRect)
        
        # Remove drawn circles.
        self.popupSurf.fill((0, 0, 0))
        
        pygame.display.update()