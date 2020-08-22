import pygame

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
        self.basic_font = pygame.font.SysFont("comicsansms", 72)

        # Text surfaces
        self.text_surfaces = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}

        render = self.basic_font.render
        for opt in points.left_options[0]:
            self.text_surfaces["left_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in points.left_options[1]:
            self.text_surfaces["left_1"].append(render(opt, 1, (0, 0, 255)))
        for opt in points.right_options[0]:
            self.text_surfaces["right_0"].append(render(opt, 1, (0, 0, 255)))
        for opt in points.right_options[1]:
            self.text_surfaces["right_1"].append(render(opt, 1, (0, 0, 255)))

        # The actual popup display surface.
        self.popupRect = self.popupSurf.get_rect()
        self.popupRect.centerx = points.screenwidth // 2
        self.popupRect.centery = points.screenheight // 2
        
        self.text_rects = {"left_0": [], "left_1": [], "right_0": [], "right_1": []}
        #for key, value in self.text_surfaces.items():
        for key in self.text_surfaces.keys():
            if key[:4] == "left":
                #for index, element in enumerate(value):
                for index in range(len(self.text_surfaces[key])):
                    textRect = self.text_surfaces[key][index].get_rect()
                    textRect.centerx = points.left_points[index][0]
                    textRect.centery = points.left_points[index][1]
                    self.text_rects[key].append(textRect)
            else:
                #for index, element in enumerate(value):
                for index in range(len(self.text_surfaces[key])):
                    textRect = self.text_surfaces[key][index].get_rect()
                    textRect.centerx = points.right_points[index][0]
                    textRect.centery = points.right_points[index][1]
                    self.text_rects[key].append(textRect)

    def draw_popup(self, variant=0):
        variant = str(variant)
        for key in self.text_surfaces.keys():
            # Check if key ends with variant number.
            if key[-1] == variant:
                for item in range(len(self.text_rects[key])):
                    textSurf = self.text_surfaces[key][item]
                    textRect = self.text_rects[key][item]
                    self.popupSurf.blit(textSurf, textRect)

        l_x, l_y, r_x, r_y = self.points.get_cursor()
        pygame.draw.circle(self.popupSurf, (255,0,0), (l_x, l_y), 5, 0)
        pygame.draw.circle(self.popupSurf, (255,0,0), (r_x, r_y), 5, 0)

        self.screen.blit(self.popupSurf, self.popupRect)
        
        # Remove drawn circles.
        self.popupSurf.fill((0, 0, 0))
        
        pygame.display.update()