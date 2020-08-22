from n_sided_polygon import polygon
from scipy import spatial
from copy import deepcopy

class PointAndOptionManager:
    def __init__(self, dimensions, options_left, options_right, FPS, hub_radius):
        # Screen and overlay dimensions.
        self.screenwidth = dimensions["screenwidth"]
        self.screenheight = dimensions["screenheight"]
        self.overlay_width = dimensions["overlay_width"]
        self.overlay_height = dimensions["overlay_height"]

        # Options and option properties
        self.left_options = {0: options_left[0], 1: options_left[1]}
        self.right_options = {0: options_right[0], 1: options_right[1]}
        self.num_options = len(self.left_options[0])

        # Polygon radius and points
        self.radius = hub_radius
        self.left_hub_center = self.screenwidth // 4
        self.right_hub_center = (self.screenwidth // 4) * 3
        self.half_screenheight = self.screenheight // 2

        # Points storage.
        self.left_points = polygon(sides=self.num_options,radius=self.radius, 
                                    translation=[self.left_hub_center, self.half_screenheight])
        
        self.right_points = polygon(sides=self.num_options, radius=self.radius, 
                                    translation=[self.right_hub_center, self.half_screenheight])

        self.cursor = {"l_x": 0, "l_y": 0, "r_x": 0, "r_y": 0}

        # Adding idle axis as an answer for nearest neighbour
        self.answers = {"left_0": deepcopy(self.left_options[0]), "left_1": deepcopy(self.left_options[1]),
                        "right_0": deepcopy(self.right_options[0]), "right_1": deepcopy(self.right_options[1])}

        for key in self.answers.keys():
            self.answers[key].append("IDLE")

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
        self.points_for_answers["left"] = deepcopy(self.left_points)
        self.points_for_answers["right"] = deepcopy(self.right_points)
        self.points_for_answers["left"].append((idle_axis[0], idle_axis[1]))
        self.points_for_answers["right"].append((idle_axis[2], idle_axis[3]))

    def get_closest_points(self):
        # If closest to idle, ignore.
        l_distance,l_index = spatial.KDTree(self.points_for_answers["left"]).query([(self.cursor["l_x"], self.cursor["l_y"])])
        r_distance,r_index = spatial.KDTree(self.points_for_answers["right"]).query([(self.cursor["r_x"], self.cursor["r_y"])])
        l_index, r_index = l_index[0], r_index[0]

        return {"left_0": self.answers["left_0"][l_index], "right_0": self.answers["right_0"][r_index],
                "left_1": self.answers["left_1"][l_index], "right_1": self.answers["right_1"][r_index]}

    def update(self, upper, variant=0):
        variant = str(variant)
        closest_points = self.get_closest_points()

        for key in closest_points.keys():
            # Check if key ends with variant number.
            if key[-1] == variant:
                # Supressing idle. Necessary for function.
                if closest_points[key] != "IDLE":
                    return self.buffer_key(closest_points[key], upper=upper)

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
