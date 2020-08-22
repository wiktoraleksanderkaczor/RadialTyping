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

        left0 = points.left_options[0]
        left1 = points.left_options[1]
        right0 = points.right_options[0]
        right1 = points.right_options[1]

        render = basic_font.render
        for opt in left0:
            self.lower_text_surfaces["left_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in left1:
            self.lower_text_surfaces["left_1"].append(render(opt, 1, (0, 0, 255)))
        for opt in right0:
            self.lower_text_surfaces["right_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in right1:
            self.lower_text_surfaces["right_1"].append(render(opt, 1, (0, 0, 255)))

        for opt in toupper(left0):
            self.upper_text_surfaces["left_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in toupper(left1):
            self.upper_text_surfaces["left_1"].append(render(opt, 1, (0, 0, 255)))
        for opt in toupper(right0):
            self.upper_text_surfaces["right_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in toupper(right1):
            self.upper_text_surfaces["right_1"].append(render(opt, 1, (0, 0, 255)))

        # The actual popup display surface.
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = points.screenwidth // 2
        self.popupRect.centery = points.screenheight // 2
        
        self.lower_text_rects = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}
        self.upper_text_rects = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}

        for key in self.lower_text_surfaces.keys():
            if key[:4] == "left":
                for index in range(len(self.lower_text_surfaces[key])):
                    textRect = self.lower_text_surfaces[key][index].get_rect()
                    textRect.centerx = points.left_points[index][0]
                    textRect.centery = points.left_points[index][1]
                    self.lower_text_rects[key].append(textRect)
            else:
                for index in range(len(self.lower_text_surfaces[key])):
                    textRect = self.lower_text_surfaces[key][index].get_rect()
                    textRect.centerx = points.right_points[index][0]
                    textRect.centery = points.right_points[index][1]
                    self.lower_text_rects[key].append(textRect)

        for key in self.upper_text_surfaces.keys():
            if key[:4] == "left":
                for index in range(len(self.upper_text_surfaces[key])):
                    textRect = self.upper_text_surfaces[key][index].get_rect()
                    textRect.centerx = points.left_points[index][0]
                    textRect.centery = points.left_points[index][1]
                    self.upper_text_rects[key].append(textRect)
            else:
                for index in range(len(self.upper_text_surfaces[key])):
                    textRect = self.upper_text_surfaces[key][index].get_rect()
                    textRect.centerx = points.right_points[index][0]
                    textRect.centery = points.right_points[index][1]
                    self.upper_text_rects[key].append(textRect)

    def draw_popup(self, variant=0, upper=False):
        variant = str(variant)

        if upper == False:
            for key in self.lower_text_surfaces.keys():
                # Check if key ends with variant number.
                if key[-1] == variant:
                    for item in range(len(self.lower_text_rects[key])):
                        textSurf = self.lower_text_surfaces[key][item]
                        textRect = self.lower_text_rects[key][item]
                        self.popupSurf.blit(textSurf, textRect)
        else:
            for key in self.upper_text_surfaces.keys():
                # Check if key ends with variant number.
                if key[-1] == variant:
                    for item in range(len(self.upper_text_rects[key])):
                        textSurf = self.upper_text_surfaces[key][item]
                        textRect = self.upper_text_rects[key][item]
                        self.popupSurf.blit(textSurf, textRect)

        l_x, l_y, r_x, r_y = self.points.get_cursor()
        pygame.draw.circle(self.popupSurf, (255,0,0), (l_x, l_y), 5, 0)
        pygame.draw.circle(self.popupSurf, (255,0,0), (r_x, r_y), 5, 0)

        self.screen.blit(self.popupSurf, self.popupRect)
        
        # Remove drawn circles.
        self.popupSurf.fill((0, 0, 0))
        
        pygame.display.update()