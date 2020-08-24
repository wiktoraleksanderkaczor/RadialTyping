from n_sided_polygon import polygon
from scipy import spatial
from copy import deepcopy

class DataManager:
    def __init__(self, dimensions, options, FPS, hub_radius):
        # Screen and overlay dimensions.
        self.screenwidth = dimensions["screenwidth"]
        self.screenheight = dimensions["screenheight"]
        self.overlay_width = dimensions["overlay_width"]
        self.overlay_height = dimensions["overlay_height"]

        # Options and option properties
        self.options = options
        self.num_options = {}
        for key in self.options.keys():
            self.num_options[key] = len(self.options[key])

        # Polygon radius and points
        self.radius = hub_radius
        self.left_hub_center = self.screenwidth // 4
        self.right_hub_center = (self.screenwidth // 4) * 3
        self.half_screenheight = self.screenheight // 2

        # Points storage.
        self.points = {}
        for key in self.options.keys():
            if key[:-2] == "left":
                self.points[key] = polygon(sides=self.num_options[key], radius=self.radius,
                                        translation=[self.left_hub_center, self.half_screenheight])
            else:
                self.points[key] = polygon(sides=self.num_options[key], radius=self.radius, 
                                        translation=[self.right_hub_center, self.half_screenheight])

        self.cursor = {"l_x": 0, "l_y": 0, "r_x": 0, "r_y": 0}

        # Adding idle axis as an answer for nearest neighbour
        self.answers = {}
        for key in self.options.keys():
            self.answers[key] = deepcopy(self.options[key]) + ["IDLE"]

        self.points_for_answers = {"left": [], "right": []}

        self.time_passed = 0
        self.last_key_buf = "IDLE"
        self.last_key_pressed = None
        self.key_buf_time = 0
        self.repeat = False

    def update_cursor(self, l_x, l_y, r_x, r_y):
        self.cursor["l_x"] = l_x
        self.cursor["l_y"] = l_y
        self.cursor["r_x"] = r_x
        self.cursor["r_y"] = r_y

    def get_cursor(self):
        l_x = self.cursor["l_x"]
        l_y = self.cursor["l_y"]
        r_x = self.cursor["r_x"]
        r_y = self.cursor["r_y"]
        return l_x, l_y, r_x, r_y

    def update_idle_points(self, idle_axis):
        # Adding idle axis as a point for nearest neighbour
        for key in self.points.keys():
            if key[:-2] == "left":
                self.points_for_answers[key] = deepcopy(self.points[key]) + \
                    [(idle_axis[0], idle_axis[1])]
            else:
                self.points_for_answers[key] = deepcopy(self.points[key]) + \
                    [(idle_axis[2], idle_axis[3])]


    def get_closest_points(self, variant):
        # If closest to idle, ignore. Only do variant number.
        l_distance,l_index = spatial.KDTree(self.points_for_answers["left_" + variant]) \
            .query([(self.cursor["l_x"], self.cursor["l_y"])])
        r_distance,r_index = spatial.KDTree(self.points_for_answers["right_" + variant]) \
            .query([(self.cursor["r_x"], self.cursor["r_y"])])
        l_index, r_index = l_index[0], r_index[0]

        return {"left": self.answers["left_" + variant][l_index], 
                "right": self.answers["right_" + variant][r_index]}

    def update(self, upper, wait_time=220, variant=0):
        variant = str(variant)
        closest_points = self.get_closest_points(variant=variant)

        # Supressing idle. Necessary for function.
        for key in closest_points.keys():
            if closest_points[key] != "IDLE":
                return self.buffer_key(closest_points[key], upper=upper, needed_time_ms=wait_time)

    def update_time(self, time_passed):
        self.time_passed = time_passed

    def buffer_key(self, key, upper, needed_time_ms=220, repeated_time_ms=500, value=None):
        # Sanity checks
        if value == None:
            value = key
        if key == False:
            return None

        # If different key, reset counters
        if value != self.last_key_pressed:
            self.key_buf_time = 0
            self.last_key_pressed = value
            self.repeat = False

        # If key repeated, adjust time for registering key
        if self.repeat == True:
            needed_time_ms = repeated_time_ms

        # If time since pressed bigger than time needed, set counters and return key
        if self.key_buf_time > needed_time_ms:
            self.last_key_buf = value
            self.repeat = True
            self.key_buf_time = 0
            if upper:
                value = value.upper()
            return value
        # Else, increment time.
        else:
            self.key_buf_time += self.time_passed
